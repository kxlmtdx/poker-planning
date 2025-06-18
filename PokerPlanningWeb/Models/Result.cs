using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    [Table("Results")]
    public class Result
    {
        [Key]
        public Guid ResultId { get; set; } = Guid.NewGuid();

        public Guid? SessionId { get; set; }

        [Required]
        public string ResultData { get; set; }

        public DateTime GeneratedDate { get; set; } = DateTime.UtcNow;

        public bool SentToMaster { get; set; } = false;

        [ForeignKey("SessionId")]
        public virtual Sessions Session { get; set; }
    }
}
