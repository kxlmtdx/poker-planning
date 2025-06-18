namespace PokerPlanningWeb.Models
{
    public class CurrentVotes
    {
        public Guid VoteId { get; set; }
        public Guid IssueId { get; set; }
        public long UserId { get; set; }
        public string Username { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public decimal Estimate { get; set; }
        public DateTime VoteDate { get; set; }
    }
}
