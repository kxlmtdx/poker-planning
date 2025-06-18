using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    public class Votes
    {
        [Key]
        public Guid VoteId { get; set; } = Guid.NewGuid();

        public Guid? IssueId { get; set; }

        public long? UserId { get; set; }

        [Required]
        public decimal Estimate { get; set; }

        public DateTime VoteDate { get; set; } = DateTime.UtcNow;

        public bool IsCurrent { get; set; } = true;

        [ForeignKey("IssueId")]
        public virtual Issues Issue { get; set; }

        [ForeignKey("UserId")]
        public virtual Users User { get; set; }

        public virtual ICollection<VoteHistory> VoteHistories { get; set; }
    }
}
