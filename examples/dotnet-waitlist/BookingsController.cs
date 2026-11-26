using Microsoft.AspNetCore.Mvc;

namespace Waitlist;

[ApiController]
[Route("bookings")]
public sealed class BookingsController(IWaitlistStore store) : ControllerBase
{
    [HttpPost("{id:long}/cancel")]
    public IActionResult Cancel(long id)
    {
        if (id <= 0)
            return BadRequest();

        var result = store.CancelAndPromote(id);
        return result.Status switch
        {
            CancellationStatus.Completed => Ok(new { result.PromotedBookingId }),
            CancellationStatus.Missing => NotFound(),
            CancellationStatus.NotConfirmed => Conflict(),
            _ => throw new InvalidOperationException("Unexpected cancellation status.")
        };
    }
}
