using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    public class VotingMessages
    {
        [Key]
        public int Id { get; set; }

        [Required]
        public Guid IssueId { get; set; }

        public int MessageId { get; set; }

        [ForeignKey("IssueId")]
        public virtual Issues Issue { get; set; }
    }
}
