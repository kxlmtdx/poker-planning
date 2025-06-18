using Microsoft.EntityFrameworkCore;
using PokerPlanningWeb.Models;

namespace PokerPlanningWeb.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<Users> Users { get; set; }
        public DbSet<Groups> Groups { get; set; }
        public DbSet<GroupMembers> GroupMembers { get; set; }
        public DbSet<Sessions> Sessions { get; set; }
        public DbSet<Issues> Issues { get; set; }
        public DbSet<Votes> Votes { get; set; }
        public DbSet<VoteHistory> VoteHistories { get; set; }
        public DbSet<Result> Results { get; set; }
        public DbSet<VotingMessages> VotingMessages { get; set; }
        public DbSet<WebSocketConnections> WebSocketConnections { get; set; }

        public DbSet<CurrentVotes> CurrentVotes { get; set; }
        public DbSet<SessionSummary> SessionSummaries { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<GroupMembers>()
                .HasKey(gm => new { gm.GroupId, gm.UserId });

            modelBuilder.Entity<Groups>()
                .HasOne(g => g.Creator)
                .WithMany(u => u.CreatedGroups)
                .HasForeignKey(g => g.CreatedBy)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<Sessions>()
                .HasOne(s => s.Creator)
                .WithMany(u => u.CreatedSessions)
                .HasForeignKey(s => s.CreatedBy)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<Issues>()
                .HasOne(i => i.Creator)
                .WithMany(u => u.CreatedIssues)
                .HasForeignKey(i => i.CreatedBy)
                .OnDelete(DeleteBehavior.Restrict);

            modelBuilder.Entity<CurrentVotes>(entity =>
            {
                entity.HasNoKey();
                entity.ToView("CurrentVotes");
            });

            modelBuilder.Entity<SessionSummary>(entity =>
            {
                entity.HasNoKey();
                entity.ToView("GetSessionSummary");
            });

            modelBuilder.Entity<Votes>()
                .Property(v => v.Estimate)
                .HasColumnType("decimal(10,2)");

            modelBuilder.Entity<VoteHistory>()
                .Property(vh => vh.PreviousEstimate)
                .HasColumnType("decimal(10,2)");

            modelBuilder.Entity<VoteHistory>()
                .Property(vh => vh.NewEstimate)
                .HasColumnType("decimal(10,2)");

            modelBuilder.Entity<Issues>()
                .Property(i => i.FinalEstimate)
                .HasColumnType("decimal(10,2)");
        }

        public decimal? CalculateMedianEstimate(Guid issueId)
        {
            var issueIdParam = new Microsoft.Data.SqlClient.SqlParameter("@IssueId", issueId);
            return Database.SqlQueryRaw<decimal?>("SELECT dbo.CalculateMedianEstimate(@IssueId)", issueIdParam)
                .AsEnumerable()
                .FirstOrDefault();
        }
    }
}
