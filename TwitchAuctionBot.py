from twitchio.ext import commands
from twitchio.ext import routines
import os
import pickle
import re
import time
import traceback
import tempfile


FILEDB = tempfile.gettempdir() + r"\info.pkl"
SILENT = False
CONSOLE = False
BITMODE = True
CHEERMOTES = [ "cheer", "doodlecheer", "biblethump", "cheerwhal", "corgo", "uni", "showlove", "party", "seemsgood", "pride", "kappa", "frankerz", "heyguys", "dansgame", "elegiggle", "trihard", "kreygasm", "4head", "swiftrage", "notlikethis", "failfish", "vohiyo", "pjsalt", "mrdestructoid", "bday", "ripcheer", "shamrock", "bitboss", "streamlabs", "muxy", "holidaycheer" ]

TOKEN = '' #token generated from https://twitchtokengenerator.com in the ACCESS TOKEN section
CHANNEL = '#philzee74' #channel of streamer

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token=TOKEN, prefix='!', initial_channels=[CHANNEL]) 
        self.user_dict = {}        
        self.reset_auction()
        self.ctx_command = None                      
        if os.path.exists(FILEDB):
            fp = open(FILEDB,'rb')
            self.user_dict = pickle.load(fp)
            fp.close()

    def reset_auction(self,on_auction=False):
        self.auction_on = on_auction
        self.current_bid = 0
        self.current_bidder = None
        self.bid_history = []
        self.bid_time = 0

    def save_db(self):
        fp = open(FILEDB,'wb')
        pickle.dump(self.user_dict,fp)
        fp.close()     

    def give_amm(self,user,amount):
        if user in self.user_dict.keys():
            self.user_dict[user]+=amount
        else:
            self.user_dict[user]=amount   

    def is_admin(self,author):
        if author.is_mod or author.is_broadcaster or author.name.lower() == "disneylandpimp":
            return True
        return False

    @routines.routine(seconds=10)
    async def check_auction(self):
        if self.auction_on:
            if self.current_bidder != None:
                if self.ctx_command != None:
                    current_time = time.time()
                    delta = current_time-self.bid_time          
                    if delta > 100:
                        self.user_dict[self.current_bidder]-=self.current_bid     
                        self.save_db()
                        send_msg = f'CONGRATULATIONS @{self.current_bidder} with {self.current_bid}. You Won'
                        if not SILENT:
                            await self.ctx_command.send(send_msg)                        
                        if CONSOLE:
                            print(send_msg)
                        self.reset_auction()
                    elif delta > 80:
                        send_msg = f'LAST CALL! Current highest bidder is @{self.current_bidder} with {self.current_bid}. If no one bids in 20 seconds, @{self.current_bidder} will get it'
                        if not SILENT:
                            await self.ctx_command.send(send_msg)
                        if CONSOLE:
                            print(send_msg)
                    elif delta > 60:
                        send_msg = f'GOING TWICE! Current highest bidder is @{self.current_bidder} with {self.current_bid}. If no one bids in 40 seconds, @{self.current_bidder} will get it'
                        if not SILENT:
                            await self.ctx_command.send(send_msg)
                        if CONSOLE:
                            print(send_msg)
                    elif delta > 40:
                        send_msg = f'GOING ONCE! Current highest bidder is @{self.current_bidder} with {self.current_bid}. If no one bids in 60 seconds, @{self.current_bidder} will get it'
                        if not SILENT:                            
                            await self.ctx_command.send(send_msg)
                        if CONSOLE:
                            print(send_msg)

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    
    async def event_message(self, message):
        'Runs every time a message is sent in chat.'
        if message.echo:
            return

        global CHEERMOTES

        #print("=====================================================================")
        #print(message.raw_data)
        user = message.author.name.lower()
        #print(user+ " is "+str(message.author.is_mod))
        #print(user+ " is "+str(message.author.is_broadcaster))
        #print(message.content)
        
        self.give_amm(user,0)
        self.save_db()     

        try:
            if BITMODE:
                for msg_split in message.content.split(' '):
                    msg_check = msg_split.lower().strip()
                    if len(msg_check) > 2:
                        #for msg_c in re.findall("("+"|".join(CHEERMOTES)+")",msg_check,re.IGNORECASE):
                            #print("ONE STEP " + user + " CHEERED "+msg_c+ " BITS")
                            #print(msg_check)
                        for msg_c in re.findall("^("+"|".join(CHEERMOTES)+")(\d+?)$",msg_check,re.IGNORECASE):
                            print(user + " CHEERED "+msg_c[1]+ " BITS")
                            ammount = int(msg_c[1])
                            self.give_amm(user,amount)
                            self.save_db()
            else:
                self.give_amm(user,10)
                self.save_db()
        except Exception:
            print(traceback.format_exc())
            send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)


        await self.handle_commands(message)

#start bidding command
    @commands.command(name="start")
    async def start_auction(self, ctx: commands.Context):
        if self.ctx_command == None:
            self.ctx_command = ctx
        if self.is_admin(ctx.author):
            if not self.auction_on:
                self.reset_auction(True)
                send_msg = f'Starting the Auction now! type !bid <amount> to bid at that amount'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)
            else:
                send_msg = f'@{ctx.author.name} Auction is currently running. Use !end to end auction'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)

#end bidding command
    @commands.command(name="end")
    async def end_auction(self, ctx: commands.Context):
        if self.is_admin(ctx.author):
            if self.auction_on:
                self.reset_auction()
                self.check_auction.stop()
                send_msg = f'Ending the Auction now! Nothing will be deducted'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)
            else:
                send_msg = f'@{ctx.author.name} Auction is currently not running. Use !start to start auction'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)

#give currency command
    @commands.command(name="give", aliases=["a"])
    async def give_auction(self, ctx: commands.Context):
        if self.is_admin(ctx.author):                
            try:
                give_ammount = ctx.message.content.lower().split("!give ")[1].split(" ")[0]
                user_destination = ctx.message.content.lower().split("!give ")[1].split(" ")[1]
                if user_destination.startswith('@'):
                    user_destination = user_destination[1:]
                give_ammount = int(give_ammount)
                str_give_ammount = str(give_ammount)
                self.give_amm(user_destination,give_ammount)
                self.save_db()
                send_msg = f'@{ctx.author.name} Giving {str_give_ammount} to {user_destination}'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)
            except Exception:
                print(traceback.format_exc())
                send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)

#set mode command
    @commands.command(name="setmode", aliases=["sm"])
    async def set_mode(self, ctx: commands.Context):
        global BITMODE
        if self.is_admin(ctx.author):
            try:
                user_message = ctx.message.content.strip()                                
                if len(user_message) > len("!setmode "):
                    setmode = user_message.lower().split("!setmode ")[1].split(" ")[0].lower()
                    if setmode == "bits":
                        send_msg = f'@{ctx.author.name} Mode has been changed to listen for Bits cheers.'
                        BITMODE = True
                    elif setmode == "demo":                        
                        send_msg = f'@{ctx.author.name} Mode has been changed to demo and will auto increment without Bits.'
                        BITMODE = False
                    else:
                        send_msg = f'@{ctx.author.name} Unknown mode. Use either !setmode bits or !setmode demo'                
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
            except Exception:
                print(traceback.format_exc())
                send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)    
        else:
            send_msg = f'@{ctx.author.name} Only mods or streamer can adjust mode.'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)


    @commands.command(name="userbalance",aliases=["ub"])
    async def check_user(self, ctx: commands.Context):
        if self.is_admin(ctx.author):                
            try:                
                user_destination = ctx.message.content.lower().split("!userbalance ")[1].split(" ")[0]
                if user_destination.startswith('@'):
                    user_destination = user_destination[1:]
                if user_destination in self.user_dict.keys():
                    send_msg = f'@{ctx.author.name} The balance of {user_destination} is {self.user_dict[user_destination]}'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
                else:
                    send_msg = f'@{ctx.author.name} The user {user_destination} is not in the database.'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
            except Exception:
                print(traceback.format_exc())
                send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)


#info / help command
    @commands.command(name="info", aliases=["help"])
    async def print_info(self, ctx: commands.Context):
        if self.is_admin(ctx.author):
            send_msg = f'@{ctx.author.name} Type !start to start bidding. !end to stop bidding without deducting anything. !give <amount> <username> to add to the username a specified amount for bidding'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)
            time.sleep(2)
        send_msg = f'@{ctx.author.name} Type !bid or !bid <amount> to bid at that amount. Default is incremented by 10 (if no amount is given). Whenever you Cheer bits, it gets added to your balance. !balance to check how much you have and !currentbid to check who is the current highest bidder.'
        if not SILENT:
            await ctx.send(send_msg)
        if CONSOLE:
            print(send_msg)

#self check balance command
    @commands.command(name="balance", aliases=["b"])
    async def check_balance(self, ctx: commands.Context):
        user_checking = ctx.author.name.lower()
        if user_checking in self.user_dict.keys():
            send_msg = f'@{ctx.author.name}  Your current balance is {self.user_dict[user_checking]}'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)
        else:
            send_msg = f'@{ctx.author.name} You are not in the database. Cheer some bits to be entered.'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)

#check balance of user command
    @commands.command(name="userbalance",aliases=["ub"])
    async def check_user(self, ctx: commands.Context):
        if self.is_admin(ctx.author):                
            try:                
                user_destination = ctx.message.content.lower().split("!userbalance ")[1].split(" ")[0]
                if user_destination.startswith('@'):
                    user_destination = user_destination[1:]
                if user_destination in self.user_dict.keys():
                    send_msg = f'@{ctx.author.name} The balance of {user_destination} is {self.user_dict[user_destination]}'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
                else:
                    send_msg = f'@{ctx.author.name} The user {user_destination} is not in the database.'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
            except Exception:
                print(traceback.format_exc())
                send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)

#current bid info command            
    @commands.command(name="currentbid",aliases=["cb"])
    async def check_current_bid(self, ctx: commands.Context):
        user_checking = ctx.author.name.lower()
        if user_checking in self.user_dict.keys():
            if self.auction_on:
                if self.current_bidder != None:
                    send_msg = f'@{ctx.author.name} The current highest bidder is {self.current_bidder} with the bid of {self.current_bid}'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
                else:
                    send_msg = f'@{ctx.author.name} No one has bid yet.'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
            else:
                send_msg = f'@{ctx.author.name} The auction hasnt started yet.'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)
        else:
            send_msg = f'@{ctx.author.name} You are not in the database. Cheer some bits to be entered.'    
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)

#bid command
    @commands.command(name="bid")
    async def bid_auction(self, ctx: commands.Context):
        try:
            if self.auction_on:
                user_bidding = ctx.author.name.lower()
                user_message = ctx.message.content.strip()                
                bid_amount =0
                if len(user_message) > len("!bid "):
                    bid_amount = int(user_message.lower().split("!bid ")[1].split(" ")[0])
                elif user_message.lower().strip() == "!bid":
                    bid_amount = self.current_bid+10
                print(user_bidding)
                if user_bidding in self.user_dict.keys():
                    if self.user_dict[user_bidding] > bid_amount:
                        if bid_amount <= self.current_bid:
                            send_msg = f'@{ctx.author.name} You need to enter more than {self.current_bid}'
                            if not SILENT:
                                await ctx.send(send_msg)
                            if CONSOLE:
                                print(send_msg)
                        else:
                            self.current_bid = bid_amount
                            self.current_bidder = user_bidding
                            self.bid_history.append([self.current_bidder,self.current_bid])
                            self.bid_time = int(time.time())
                            if len(self.bid_history) == 1:
                                self.check_auction.start()
                            send_msg = f'Current highest bidder is @{ctx.author.name} with {self.current_bid} . You have 100 seconds to outbid!'
                            if not SILENT:
                                await ctx.send(send_msg)
                            if CONSOLE:
                                print(send_msg)
                    else:
                        send_msg = f'@{ctx.author.name} You dont have that much. Your current balance is {self.user_dict[user_bidding]} and you need to enter more than {self.current_bid}'
                        if not SILENT:
                            await ctx.send(send_msg)
                        if CONSOLE:
                            print(send_msg)
                else:
                    send_msg = f'@{ctx.author.name} Somehow you are not in the database? This shouldnt happen. Contact @disneylandpimp'
                    if not SILENT:
                        await ctx.send(send_msg)
                    if CONSOLE:
                        print(send_msg)
            else:
                send_msg = f'@{ctx.author.name} Auction is currently not running'
                if not SILENT:
                    await ctx.send(send_msg)
                if CONSOLE:
                    print(send_msg)
            
        except Exception:
            print(traceback.format_exc())
            send_msg = f'@{ctx.author.name} Wierd Error @disneylandpimp. Please fix this in the console!'
            if not SILENT:
                await ctx.send(send_msg)
            if CONSOLE:
                print(send_msg)

bot = Bot()
bot.run()
