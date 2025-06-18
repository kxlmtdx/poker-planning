using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.RegularExpressions;

namespace PokerPlanningWeb.Models
{
    public class GroupMembers
    {
        [Key, Column(Order = 0)]
        public long GroupId { get; set; }

        [Key, Column(Order = 1)]
        public long UserId { get; set; }

        public DateTime JoinDate { get; set; } = DateTime.UtcNow;

        [ForeignKey("GroupId")]
        public virtual Groups Group { get; set; }

        [ForeignKey("UserId")]
        public virtual Users User { get; set; }
    }
}
