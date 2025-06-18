using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.RegularExpressions;

namespace PokerPlanningWeb.Models
{
    public class Sessions
    {
        [Key]
        public Guid SessionId { get; set; } = Guid.NewGuid();

        public long? GroupId { get; set; }

        public long? CreatedBy { get; set; }

        public DateTime StartDate { get; set; } = DateTime.UtcNow;

        public DateTime? EndDate { get; set; }

        [StringLength(20)]
        public string? Status { get; set; } = "Active";

        [ForeignKey("GroupId")]
        public virtual Groups Group { get; set; }

        [ForeignKey("CreatedBy")]
        public virtual Users Creator { get; set; }

        public virtual ICollection<Issues> Issues { get; set; }
        public virtual ICollection<Result> Results { get; set; }
        public virtual ICollection<WebSocketConnections> WebSocketConnections { get; set; }
    }
}
