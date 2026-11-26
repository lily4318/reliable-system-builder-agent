using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Mvc;

namespace Waitlist;

[ApiController]
[Route("admin/bookings")]
public sealed class EligibilityController(IWaitlistStore store, IConfiguration configuration) : ControllerBase
{
    public sealed record ReviewRequest(bool? Eligible);

    [HttpPut("{id:long}/eligibility")]
    public IActionResult Review(long id, ReviewRequest request)
    {
        var key = configuration["WaitlistAdminKey"];
        if (string.IsNullOrWhiteSpace(key)
            || !Request.Headers.TryGetValue("X-Waitlist-Admin-Key", out var supplied)
            || supplied.Count != 1
            || !CryptographicOperations.FixedTimeEquals(
                SHA256.HashData(Encoding.UTF8.GetBytes(key)),
                SHA256.HashData(Encoding.UTF8.GetBytes(supplied[0] ?? string.Empty))))
            return Unauthorized();

        if (id <= 0 || request.Eligible is not bool eligible)
            return BadRequest();

        return store.ReviewEligibility(id, eligible) switch
        {
            EligibilityReviewStatus.Updated => NoContent(),
            EligibilityReviewStatus.Missing => NotFound(),
            EligibilityReviewStatus.NotWaiting => Conflict(),
            _ => throw new InvalidOperationException("Unexpected eligibility review status.")
        };
    }
}
