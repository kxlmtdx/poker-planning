using PokerPlanningWeb.Models;
using System.ComponentModel.DataAnnotations;

public class Users
{
    [Key]
    public long UserId { get; set; }

    [StringLength(100)]
    public string Username { get; set; }

    [StringLength(100)]
    public string FirstName { get; set; }

    [StringLength(100)]
    public string LastName { get; set; }

    public bool IsScrumMaster { get; set; } = false;

    public DateTime RegistrationDate { get; set; } = DateTime.UtcNow;

    public virtual ICollection<GroupMembers> GroupMembers { get; set; }
    public virtual ICollection<Groups> CreatedGroups { get; set; }
    public virtual ICollection<Sessions> CreatedSessions { get; set; }
    public virtual ICollection<Issues> CreatedIssues { get; set; }
    public virtual ICollection<Votes> Votes { get; set; }
    public virtual ICollection<WebSocketConnections> WebSocketConnections { get; set; }
}