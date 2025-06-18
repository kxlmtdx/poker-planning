using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    public class VoteHistory
    {
        [Key]
        public Guid HistoryId { get; set; } = Guid.NewGuid();

        public Guid? VoteId { get; set; }

        public decimal? PreviousEstimate { get; set; }

        [Required]
        public decimal NewEstimate { get; set; }

        public DateTime ChangeDate { get; set; } = DateTime.UtcNow;

        [ForeignKey("VoteId")]
        public virtual Votes Vote { get; set; }
    }
}
