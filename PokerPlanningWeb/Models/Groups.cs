using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PokerPlanningWeb.Models
{
    public class Groups
    {
        [Key]
        public long GroupId { get; set; }

        [StringLength(200)]
        public string GroupName { get; set; }

        public long? CreatedBy { get; set; }

        public DateTime CreationDate { get; set; } = DateTime.UtcNow;

        public bool IsActive { get; set; } = true;

        [ForeignKey("CreatedBy")]
        public virtual Users Creator { get; set; }

        public virtual ICollection<GroupMembers> GroupMembers { get; set; }
        public virtual ICollection<Sessions> Sessions { get; set; }
    }
}
