using System.Net;
using Microsoft.Data.Sqlite;
using Waitlist;

var builder = WebApplication.CreateBuilder(args);
var database = builder.Configuration["WaitlistDatabase"]
    ?? throw new InvalidOperationException("Provide the path to a synthetic waitlist database.");
builder.WebHost.ConfigureKestrel(options => options.Listen(IPAddress.Loopback, 0));
builder.Services.AddControllers();
builder.Services.AddScoped<IWaitlistStore>(_ => new SqliteWaitlistStore(
    new SqliteConnectionStringBuilder
    {
        DataSource = Path.GetFullPath(database),
        Mode = SqliteOpenMode.ReadWrite,
        ForeignKeys = true,
        DefaultTimeout = 5
    }.ToString()));

var app = builder.Build();
app.MapControllers();
app.Run();
