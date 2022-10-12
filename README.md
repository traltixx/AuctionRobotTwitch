# AuctionRobotTwitch
Code for a Simple Auction Bot for Twitch

Requires Python 3.8+ and the TwitchIO module.

Get the twitch API token from https://twitchtokengenerator.com in the ACCESS TOKEN section

The Silent global var controls if anything gets printed in twitch chat.
The Console global var controls if anything gets printed in normal console.
The Bitmode global var controls if the balance is increased by bits or by normal chatting.

Available commands:
 - !start = this is to start the auction. This command is available for mods and the streamer themself only.
 - !end = this is to end the auction and not deduct or penalize anything. This command is available for mods and the streamer themself only.
 - !give <amount> <username> or !g <amount> <username>  = gives the user the amount. This command is available for mods and the streamer themself only.
 - !setmode [bits|demo] or !sm [bits|demo]= changes the mode to either demo or bits. Demo mode increases the balance by chatting. Bits mode increases the balance by cheering bits
 - !info or !help = prints some help messages about basic usage.
 - !balance or !b = gives the balance of the person who ran the command. 
 - !userbalance <username> or !ub <username> = gives the balance of the username in the command.
 - !currentbid or !cb = Gives info on the current auction and highest bidder (if any)
 - !bid = bid at 10 more than the highest bidder
 - !bid <amount> = bid at the given amount
 
 
 Donate :
 
 ETH : 0xa63dc75a049b32b2a71ca50813cba003610eb4eb
 BTC : 12trQbgoKCmYsGcAKr9Kkq8gRmAsfznhNS
 LTC : MKBCrPxmc118BVPCLJBYXCJ5i5DZBzPy66
