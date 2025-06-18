namespace PokerPlanningWeb.Models
{
    public class SessionSummary
    {
        public Guid IssueId { get; set; }
        public string Title { get; set; }
        public string Status { get; set; }
        public decimal? FinalEstimate { get; set; }
        public int VoteCount { get; set; }
        public decimal? AverageEstimate { get; set; }
        public decimal? MedianEstimate { get; set; }
    }
}
