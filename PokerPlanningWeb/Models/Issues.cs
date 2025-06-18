using PokerPlanningWeb.Controllers;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    public class Issues
    {
        [Key]
        public Guid IssueId { get; set; } = Guid.NewGuid();

        public Guid? SessionId { get; set; }

        [Required, StringLength(500)]
        public string Title { get; set; }

        public string? Description { get; set; }

        public long? CreatedBy { get; set; }

        public DateTime CreationDate { get; set; } = DateTime.UtcNow;

        [StringLength(20)]
        public string Status { get; set; } = "Pending";

        public decimal? FinalEstimate { get; set; }

        public DateTime? FinalizedDate { get; set; }

        [ForeignKey("SessionId")]
        public virtual Sessions Session { get; set; }

        [ForeignKey("CreatedBy")]
        public virtual Users Creator { get; set; }

        public virtual ICollection<Votes> Votes { get; set; }
        public virtual ICollection<VotingMessages> VotingMessages { get; set; }
    }
}
