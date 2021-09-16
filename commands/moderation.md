---
description: Docs For Moderation Commands
---

# Moderation

Moderation Commands available as of now are `kick`, `ban`, `unban`, `mute`, & `unmute`.  
Click the part on the right to skip there.  
  
More moderation commands will be added in future.   
If you have ideas send it to me on discord **Mr.Natural\#3549**

## Kick Command

**Description**  
This Command kicks the user/member from the guild/server.

**Usage**  
`#kick <user> [reason]`

* `<user>` can be id of the user, the tag \(eg- Mr.Natural\#3549\), or straight up mention the user.
* `[reason]` is the reason to kick the user this reason is sent to audit log and the kicked user in their DMs. The reason Is "No Reason Provided" by default.

**Example**  
`#kick Dummy#6969` or `#kick Dummy#6969 Posting Suspicous Links In Chat.`

## Ban Command

**Description**  
This Command unbans **previously banned** user/member from the guild/server.

**Usage**  
`#ban <user> [reason]`

* `<user>` can be id of the user, the tag \(eg- Mr.Natural\#3549\), or straight up mention the user.
* `[reason]` is the reason to kick the user this reason is sent to audit log and the kicked user in their DMs. The reason Is "No Reason Provided" by default.

**Example**  
`#ban Dummy#6969` or `#ban Dummy#6969 Memes In General` 

## **Unban Command**

**Description**  
This Command unbans **previously banned** user/member from the guild/server.

**Usage**  
`#unban <user>`

* `<user>` can only be the id or the tag \(eg- Mr.Natural\#3549\) of the user.

**Example**  
`#unban Dummy#6969`

## Mute Command

**Description**  
This Command mutes a user/member that he/she can't talk in chat.   
**Note:-** The mute role should be name exactly "Muted" for this to work. We are working on database currently for you to change it to whatever.

**Usage**  
`#mute <user> [time]`

* `<user>` can be id of the user, the tag \(eg- Mr.Natural\#3549\), or straight up mention the user.
* `[time]` is the value like 10s for 10 seconds, 1m for 1 minute, 1h for hour, 1d for 1 day. If the time isn''t provided user/member is muted undefinetly. After the provided time user will be auto-unmuted.

**Example**  
`#mute Dummy#6969` or `#mute Dummy#6969 1h 20m`

## Unmute Command

**Description**  
This Command unmutes a previously muted user else before the provided time or if the user was muted undefinetly.   
**Note:-** The mute role should be name exactly "Muted" for this to work. We are working on database currently for you to change it to whatever.

**Usage**  
`#unmute <user>`

* `<user>` can be id of the user, the tag \(eg- Mr.Natural\#3549\), or straight up mention the user.

**Example**  
`#unmute Dummy#6969`

