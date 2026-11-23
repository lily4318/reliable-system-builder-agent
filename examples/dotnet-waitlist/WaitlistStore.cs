using Microsoft.Data.Sqlite;

namespace Waitlist;

public enum CancellationStatus { Completed, Missing, NotConfirmed }

public sealed record CancellationResult(CancellationStatus Status, long? PromotedBookingId = null);

public interface IWaitlistStore
{
    CancellationResult CancelAndPromote(long bookingId);
}

public sealed class SqliteWaitlistStore(string connectionString) : IWaitlistStore
{
    public CancellationResult CancelAndPromote(long bookingId)
    {
        using var connection = new SqliteConnection(connectionString);
        connection.Open();
        // Acquire the write reservation before observing the booking or queue.
        using var transaction = connection.BeginTransaction(deferred: false);
        using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.Parameters.AddWithValue("$id", bookingId);
        command.CommandText = "SELECT promoted_id FROM cancellation WHERE booking_id = $id";
        switch (command.ExecuteScalar())
        {
            case long promoted:
                return new(CancellationStatus.Completed, promoted);
            case DBNull:
                return new(CancellationStatus.Completed);
        }

        command.CommandText = """
            UPDATE booking SET status = 'cancelled'
            WHERE id = $id AND status = 'confirmed'
            RETURNING slot_id
            """;
        if (command.ExecuteScalar() is not long slotId)
        {
            command.CommandText = "SELECT 1 FROM booking WHERE id = $id";
            return new(command.ExecuteScalar() is null
                ? CancellationStatus.Missing
                : CancellationStatus.NotConfirmed);
        }

        command.Parameters.AddWithValue("$slot", slotId);
        command.CommandText = """
            UPDATE booking SET status = 'confirmed'
            WHERE id = (
                SELECT id FROM booking
                WHERE slot_id = $slot AND status = 'waiting' AND eligible = 1
                ORDER BY queue_sequence, id LIMIT 1
            )
            RETURNING id
            """;
        var promotedBookingId = (long?)command.ExecuteScalar();

        command.Parameters.AddWithValue("$promoted", (object?)promotedBookingId ?? DBNull.Value);
        command.CommandText = "INSERT INTO cancellation VALUES ($id, $promoted)";
        command.ExecuteNonQuery();
        transaction.Commit();
        return new(CancellationStatus.Completed, promotedBookingId);
    }
}
