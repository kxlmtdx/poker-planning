using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    //а оно мне надо?
    public class WebSocketConnections
    {
        [Key, StringLength(100)]
        public string ConnectionId { get; set; }

        public long? UserId { get; set; }

        public Guid? SessionId { get; set; }

        public DateTime ConnectionDate { get; set; } = DateTime.UtcNow;

        public DateTime LastActivity { get; set; } = DateTime.UtcNow;

        public bool IsActive { get; set; } = true;

        [ForeignKey("UserId")]
        public virtual Users User { get; set; }

        [ForeignKey("SessionId")]
        public virtual Sessions Session { get; set; }
    }
}