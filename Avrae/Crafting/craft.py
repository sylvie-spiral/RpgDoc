embed 
<drac2>
# include the libraries
using(
    toolLib="6251e20c-7545-4c63-92af-31e0745f2b0c",
    bagLib="4119d62e-6a98-4153-bea9-0a99bb36da2c",
    vwLib="166d367e-e84d-436c-b099-feadbdabd25d"
)

# variable instantiation
craftLog    = load_json(get('craftLogs','{"projects": [{"name":"","baseItem":"","resource":"","total":"","crafted":"","tFinish":"","helper":[{"name":"","stat":""}]}]}')).projects
projectList = load_json(get('craftProjects','{"projects": [{"name":"","resource":"","success":"","total":"","crafted":"","tStart":"","isActive":""}]}')).projects
weaponData  = load_json(get_gvar("24a48cae-8629-4c75-9b22-51ca1215a743"))
a, out, ch  = argparse(&ARGS&), [''], character()
cc = "Daily Work"
munRes = "Mundane Resource"
rIndicator = ":"
CR = "Number of Resources"
lvl = level
race = ch.race
ft = "Founder's Token"
dvi = "Divine Inspiration"
char_prof_bonus = character().stats.prof_bonus

userTiers = vwLib.getUserTier()        # array of item tiers
toolLib.ensure_compatibility()         # convert character if needed.
tools = toolLib.char_proficiencies() # dictionary of proficiency, 0, .5, 1 or 2.

# Logical check's intial setting False

# remove ones not needed by toolLib
ftCheck = False
halfLuck = False
reliableTalent = False
ftUse = False
dviUse = False
artBlessing = False
medIntuition = False
everHospit = False
giftScribe = False
foundry = False

#counter instantiation
if not ch.cc_exists(cc):
    ch.create_cc(cc,0,1,'long','bubble')
    ch.set_cc(cc,1)
else:
    if not ch.cc_exists(munRes):
        if ch.cc_exists(CR):
            oldRes = ch.get_cc(CR)
            ch.create_cc(munRes,0,None,None)
            ch.set_cc(munRes,oldRes,True)
        else: 
            ch.create_cc(munRes,0,None,None)
            ch.set_cc(munRes,0)
v = ch.cc_exists(cc) and ch.get_cc(cc) >= 1

#Inputs
toolUsed = a.last('u',"default")
item     = a.last('c',"active")
aId      = a.last('a') if a.last('a') else None
target   = a.last('t') if a.last('t') else None
customMats = int(a.last('m')) if a.last('m') else ""
cd = "Days Crafting"

#channel Data
runIn = ctx.channel.id

# List of all allowed channels;
all_channels = load_json(get_gvar("6392559f-4c8b-4f32-a884-6715cb916fea")) 

emojiCrafting = ['🔨','⚒️','🛠️']

# allow in all channels
allowedChannel = (runIn in all_channels) or (ctx.channel.name[0] in emojiCrafting)

#Priority error checks such as no Daily Work, etc before any other Errors..
if not allowedChannel:
    text.append('* <#1254623099895287898>')
    fmt =  ', '.join(emojiCrafting)
    text.append(f'* Any channel marked with {fmt} to the left of the name.')

    text = "\n".join(out)

    return f''' -title "{name} attempts to perform their daily work." -f ':no_entry_sign: Daily Tasking Error| This command can only be ran in the appropriate channels. This is restricted to:\n {text}' '''

if not v:
    return f''' -title ":x: Error: No more Daily Work uses!" -desc "{name} has already done their {cc} for this day. If this is truly incorrect, make sure to take a long rest before running this again." -f "{cc}|{ch.cc_str(cc)}" '''
if a.last('t') and not a.last('c'):
    return f''' -title ":x: Error: No item name input found!" -desc "Assisting other players need an item input. Please try again and make sure you run `!craft -c \\"item name\\" -t @playerName.`" '''


#------------------------ITEM SECTION-----------------------
#ItemInput[1]: if no -c input from user
if item == "active":
    if projectList[0].name != "":
        for project in projectList:
            if project.isActive == "True":
                item = project.name
    else:
        return f''' -title ":x: Error: You don't have any Active Project!" -desc "Please, make sure you have an active project before running `!craft`. You can check your current Active Project by running `!craft status`.\n\nCreate a new project by running `!craft -c \"itemName\"`. Or you can also switch between projects by running `!craft -c \"itemName\"` if the item is already on your crafting project list." -f "{cc}|{ch.cc_str(cc)}" '''

#ItemInput[2]: -c input exists 
else:
    hit   = ''
    match = []
    for itemName in weaponData:
        if item.lower() == itemName.lower():
            hit      = itemName
        elif item.lower() in itemName.lower():
            itemName = itemName.replace("'", "‘")
            match.append(f"{itemName}")
    
    if hit != '':
        item = hit
    elif match == []:
        return f''' -title ":x: Error: No craftable item matches!" -desc "**Your Input**: {item}\nPlease make sure the item you wish to craft is listed in the Guide!" -f "{cc}|{ch.cc_str(cc)}" '''
    elif len(match) == 1:
        item = match[0].replace("‘","'")
    else:
        matchDisp   = ''  
        for x in match:
            xDisp    = f'{x}:\n `!craft -c \\"' + f'{x}' + '\\"`\n\n'
            matchDisp += xDisp 
        
        #limits the display list to x characters
        if len(match) > 5:
            return f''' -title ":x: Error: Too many craftable item matches found!" -desc "**Your Input:** {item}\n**Matches Found:** {len(match)} items\n\nPlease specify your item name better based on what written in the Guide." -f "{cc}|{ch.cc_str(cc)}" ''' 
        else:    
            return f''' -title "Multiple craftable item matches found!" -desc "**Your Input:** {item}\n**Matches Found:** {len(match)} items\n\n**Please use one of the following commands:**\n {matchDisp.replace("‘","'")}\n***Note**: item matches are pulled from all craftable items regardless your character Skill Level, Proficiency, and Resources.*"'''
  
#optional attributes input
if a.last('a'):
    if len(aId) < 3:
        return f''' -title ":x: Error: Invalid attribute name!" -desc "The following list of attribute names is acceptable for the command: str, dex, con, int, wis, cha." '''   
    if aId.lower() in "strength":
        attribute = strengthMod
    else:
        if aId.lower() in "dexterity":
            attribute = dexterityMod
        else:
            if aId.lower() in "constitution":
                attribute = constitutionMod
            else:
                if aId.lower() in "intelligence":
                    attribute = intelligenceMod
                else:
                    if aId.lower() in "wisdom":
                        attribute = wisdomMod
                    else:
                        if aId.lower() in "charisma":
                            attribute = charismaMod
                        else:
                            return f''' -title ":x: Error: Invalid attribute name!" -desc "The following list of tool names is acceptable for the command: str, dex, con, int, wis, cha." '''  
else:
    attribute = ""


#---------------------------------------------------------------------------TOOLS SECTION
#get proficiency and expertise for tools.
#check Tool vs. Item allowable tool
wTool      = weaponData[item].tools

#ToolsInput[1]: Input -u exists
if a.last('u'):    
    # Set up tools & skills    
    found = False
    matches = toolLib.matching_tools(toolUsed)
    found = (Len(matches) == 1)
    
    if found:
        # find best matching attribute
        attrName = toolLib.best_ability(matches[0])
        attDisp = toolLib.tool_proficiency_str(matches[0])
    else:
        return f''' -title ":x: Error: Invalid tool name!" -desc "The following list of tool names is acceptable for the command: smith, alchemist, brewer, woodcarver, potter, glassblower, calligrapher, carpenter, cobbler, cook, jeweler, leatherworker, mason, painter, tinker, weaver, poisoner, herbalism."  -f "{cc}|{ch.cc_str(cc)}" '''                    
    if tool not in wTool:
        return f''' -title ":x: Error: Incorrect tool usage!" -desc "{name} attempts to craft a {item} using {tool}, however that tool is not able to craft that item.\nThe following tools can be used to create a {item}: {wTool}" -f "{cc}|{ch.cc_str(cc)}" '''        

#ToolsInput[2]: Input not exists, automate tools
else:
    #create an array consists of tools needed to create the item

    toolNeed   = []
    
    #turns wTool into an array, and trims any extra spaces.  
    wToolList = wTool.split(",")
    for tl in wToolList:
        toolNeed.append(tl.strip())
    
    #find the highest score (attribute+prof/expt) of tool usage
    toolScore = []
    for tl in toolNeed:
        matches = toolLib.matching_tools(tl)
        found = (Len(matches) == 1)

        if found:
            match = matches[0]
            # is character proficient? Disallow Jack of All Trades here.
            if tools[match] >= 1:
                # find best matching attribute
                attrName = toolLib.best_ability(match)
                attDisp = toolLib.tool_proficiency_str(match)

                # get total modifier:
                mod = character().skills[attrName]  # ability modifier
                pb = char_prof_bonus * tools[match]             # for this prof
                toolScore.append(mod + pb)
    
    #grab the tool/attribute that has the highest score
    maxValue = max(toolScore)
    maxIndex = toolScore.index(maxValue)
    tool     = toolNeed[maxIndex]
    
   #If tools required not proficient
    toolNeedDisp    = "- "+"\n - ".join(toolNeed)
    if max(toolScore) == 0:
        return f''' -title ":x: Error: Not proficient in required tools!" -desc "**Item to craft:** {item}\n**Required tool proficiency:**\n{toolNeedDisp}\n\n{name} neither have proficiency nor expertise in one of the tools needed to craft a(n) '{item}'!" -f "Your tool proficiency:|**Prof**: {"None" if toolProf =="{}" else toolProf}\n**Expt**: {"None" if toolExpt=="{}" else toolExpt}" -f "Adding Tool Proficiency|`!tool pro \\"tool name\\"`|inline" -f "Adding Tool Expertise|`!tool exp \\"tool name\\"`|inline" -f "{cc}|{ch.cc_str(cc)}" '''
    
#check tool profs
toolKey = toolLib.matching_tools(tool)[0]

if (tools[toolKey] < 1):
    return f''' -title ":x: Error: Not proficient in selected tools!" -desc "**Tool input:**\n{toolUsed}\n\n{name} neither have proficiency nor expertise in {toolUsed}!" -f "Your tool proficiency:|**Prof**: {"None" if toolProf =="{}" else toolProf}\n**Expt**: {"None" if toolExpt=="{}" else toolExpt}" -f "Adding Tool Proficiency|`!tool pro \\"tool name\\"`|inline" -f "Adding Tool Expertise|`!tool exp \\"tool name\\"`|inline" -f "{cc}|{ch.cc_str(cc)}" '''      

#---------------------------------------------------------------------------PLAYER TIER SECTION
# check tier against item
wSkill   = weaponData[item].skillLevel  # these need updated

if not wSkill in userTiers:
    return f''' -title ":x: Error: Insufficient skill level!" -desc "{name} attempts to make a {item} but their level is too low to make the item, which requires the {wSkill} skill level ({userTiers.join(', ')})." '''
        
#checking for item restriction: 
#currently the only restriction is for gunslinger fighters. 
restrict = weaponData[item].restrict
restrictDets = ["",""]
sc = get("subclass", "{}")
if restrict != "":
    restrictDets = restrict.split("-")
if restrictDets[0] == "subclass":
    if restrictDets[1] not in sc:
       return f''' -title ":x: Error: Incorrect Knowledge!" -desc "{name} attempts to make a {item} but it is restricted to {restrictDets[1]}s " ''' 

#---------------------------------------------------------------------------ROLL CHECK VARIABLES   
#[Artisan's Blessing]
mHuman =  ["Mark of Making Human"] 
artBlessingDisp = ""
if race in mHuman:
    artBlessing = True
    artBlessingDisp = "Artisan's Blessing|When you make an Arcana check or an ability check involving artisan's tools, you can roll a d4 and add the number rolled to the ability check."
    
#[Medical Intuition]
mHHalfling =  ["Mark of Healing Halfling"] 
mIntuitionDisp = ""
if race in mHHalfling:
    if tool == "Herbalism Kit":
        medIntuition = True
        mIntuitionDisp = "Medical Intuition|When you make a Wisdom (Medicine) check or an ability check using an herbalism kit, you can roll a d4 and add the number rolled to the ability check."

#[Gifted Scribe]
sGnome =  ["Mark of Scribing Gnome"] 
giftedScribeDisp = ""
if race in sGnome:
    if tool == "Calligrapher's Supplies":
        giftScribe = True
        giftedScribeDisp = "Gifted Scribe|When you make an Intelligence (History) check or an ability check using calligrapher's supplies, you can roll a d4 and add the number rolled to the ability check.."
    
#[Ever Hospitable]
mHaHalfling =  ["Mark of Hospitality Halfling"] 
everHospitableDisp = ""
if race in mHaHalfling:
    if tool == "Brewer's Supplies" or tool == "Cook's Utensils":
        everHospit = True
        everHospitableDisp = "Ever Hospitable|When you make a Charisma (Persuasion) check or an ability check involving brewer's supplies or cook's utensils, you can roll a d4 and add the number rolled to the ability check."

#[2] Crafting time and Resources
adv,dis,fireRune,SGL = "adv" in a and not "dis" in a,"dis" in a and not "adv" in a, "fireRuneCheck" in a, "sgl" in a
resNeeded = weaponData[item].resources if not customMats or customMats == "True" else customMats
craftTime = weaponData[item].craftingTime

#[3] Founder's Token
# create founder's token and check if runnable
ftDisp = ""
for x in tierList.founder:
    if x == cDisc:
        # Founder Token token creation, set, and check
        if not ch.cc_exists(ft):
            ch.create_cc(ft,0,1,"long","bubble")
            ch.set_cc(ft,1, True)
        ftCheck = ch.cc_exists(ft)
        ftActive = ch.get_cc(ft)>=1

if "founder".lower() in a:
    ftUse = True
    if ftCheck:
        if ftActive:
            ch.mod_cc(ft,-1)
            adv = True
            ftDisp = "Founder's Token|Thank you for supporting RealmSmith from the beginning of the server, Take advantage on this roll in our appreciation." 
        else: 
            ftDisp = ":no_entry_sign: Founder's Token Error|Thank you for supporting RealmSmith from the beginning of the server, you have already used your token today, if this is in error please contact a Realmwatcher or Avrae Technomancer for assistance in a possible re-roll."
else:
    ftDisp = ""

# [4] Divine Inspiration
if "dInspiration".lower() in a or "dInspiration" in a:
    dviUse = True
    dviCheck = ch.cc_exists(dvi)
    dviActive = ch.get_cc(dvi)==1
    if dviCheck:
        if dviActive:
            ch.mod_cc(dvi,-1)
            adv = True
            dviDisp = "Divine Inspiration|The six have provided you this daily inspiration by your generousity at their temple in Herethis."
        else: 
            dviDisp = ":no_entry_sign: Function Error|you have either taken a long rest, or do not have a Divine Inspiration. A divine inspiration is obtained at the Temple of the Six for 5 gold."
else:
    dviDisp = ""
#setting up resources held variable. Errors out with "0" if cc doesn't exist. 
if ch.cc_exists(munRes):
    resHeld = ch.get_cc(munRes) 
else:
    return f''' -title ":x: Error: Insufficient resources!" -desc "You do not have enough resources to craft a(n) {item}; you need {resNeeded} to do so, and you have {resHeld} on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    
DC = 12

#[2] CVAR Time variables
anchorPts   = 1627232400 #Jul 26, 00:00:00 (GMT+7)
timeHrs     = (time()-anchorPts)/3600
tStart      = (''+timeHrs).split('.')[0]
pjCraft = "self"

#[3] other variables needed to declare for craftProjects CVAR
pjSwitch    = False
n           = 0
for project in projectList:
    n += 1
    if project.name == item:
        pjCount     = n-1
        pjSwitch    = True
        success     = int(project.success)
        adjCraftTime= int(project.total)

# pick up everything from toolLib
d20String = toolLib.tool_check_dice_str(tool, aId, adv, dis)
d20String = d20String + (( f'+{proficiencyBonus}' if fireRune else " ")+(" [Fire Rune]" if fireRune else " ")) + (( f'+1' if SGL else " ")+(" [Stone of Good Luck]" if SGL else " ")) + (( f'+1d4' if artBlessing else " ")+(" [Artisan's Blessing]" if artBlessing else " ")) + (( f'+1d4' if medIntuition else " ")+(" [Medical Intuition]" if medIntuition else " ")) + (( f'+1d4' if everHospit else " ")+(" [Ever Hospitable]" if everHospit else " ")) + (( f'+1d4' if giftScribe else " ")+(" [Gifted Scribe]" if giftScribe else " "))
check   = vroll(sroll)
crit    = check.result.crit
cStatus = ":x: **Check status:** Failed"

#[5] variables specific for displays/output
attDisp = f"({aId.upper()})" if a.last('a') else attDisp
attOR   = "" if not a.last('a') else f"custom attribute input"
matOR   = "" if not a.last('m') else f"custom material input"
ctmDisp = "" if not attOR and not matOR else f"*This command is run with {attOR if attOR else ''}{' and ' if attOR and matOR else ''}{matOR if matOR else ''}!*\n\n"


#---------------------------------------------------------------------------CRAFTING ROLL CHECKS
#[1] IF YOU ARE ASSISTING SOMEONE ELSE'S PROJECT
if a.last('t'):
    if "@" not in target:
        return f''' -title ":x: Error: Invalid player name input format!" -desc "Assisting other players need a target input format with @playerName to ping the player. Please try again and make sure you run `!craft -c \\"item name\\" -t @playerName.`" '''
    #checking to see if helping is allowable, 
    if weaponData[item].craftingTime < 15:
        return f''' -title ":x: Error: Crafting project '{item}' cannot be assisted!" -desc "Only crafting projects that requires 14 days or more can be helped with another player of same tier. Please check the Guide section 'Crafting the Vistani Way' for more information. {item} default crafting time is `{weaponData[item].craftingTime}` days." '''
    ch.mod_cc(cc,-1,True)
    cmdStat = "fail"
    #roll results
    if crit == 2:
        cStatus      = ":x: **Check status:** Critical Fail"
        adjCraftTime = 1
        cmdStat = "critfail"
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            success = 2
            cmdStat = "crits"
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            success = 1
            cmdStat = "success"
    else:
        success = 0
    #required variables for !craft helped command
    cmdPing = "@" + ctx.author
    if cmdStat != "fail":
        cmdHelp = f"Please make sure {target} run below command:\n ``!craft helped -c \\\"{item}\\\" -t \\\"{name}\\\" -s {cmdStat} -p {cmdPing}``" 
    if cmdStat == "fail": 
        cmdHelp = "The check result is a failure. No command needed to run by the player you helped."
    
    out.append(f''' -title "{name} works to help another crafter\'s {item} using their {tool}." ''')
    out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**Tool check {attDisp}:** {check}\n{cStatus}\n**Crafter helped:** {target}" -f "Realmsmith's Crafting Guide|In order to craft an item you will be able to make a single check per long rest to see if you are successful in crafting or not. Each day your character may make a Proficiency Check with the associated tools/kit. With a successful total roll of 12 or higher you succeed in crafting for that day. Heroes of the Realm and higher only require a successful total roll of 10 or higher. Rolling a Natural 20 counts for two successful days of crafting, whereas a Natural 1 results in an additional failed day above the one you rolled for." -f "You are assisting another player|{cmdHelp}" ''')
    if halfLuck:
        out.append(f''' -f "{hLuck}" ''')
    if reliableTalent:
        out.append(f''' -f "{rTalentDisp}" ''')
    if giftScribe:
        out.append(f''' -f "{giftedScribeDisp}" ''')
    if medIntuition:
        out.append(f''' -f "{mIntuitionDisp}" ''')
    if everHospit:
        out.append(f''' -f "{everHospitableDisp}" ''')
    if artBlessing:
        out.append(f''' -f "{artBlessingDisp}" ''')
    if foundry:
        out.append(f''' -f "{oDisp}" ''')    
    if ftUse:
        out.append(f''' -f "{ftDisp}" ''')
        if ftActive:
            out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
        else:
            out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
    if dviUse:
        out.append(f''' -f "{dviDisp}" ''')
        if dviActive:
            out.append(f''' -f "{dvi} (-1)|{ch.cc_str(dvi)}" ''')
        else:
            out.append(f''' -f "{dvi}|{ch.cc_str(dvi)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''')
    return '\n'.join(out)    
    
#[2] CRAFT FOR SELF, IF THE PROJECT ALREADY EXISTS
elif pjSwitch == True:
    delCvar = False
    ch.mod_cc(cc,-1,True)
    
    #roll results
    if crit == 2:
        cStatus      = ":x: **Check status:** Critical Fail"
        adjCraftTime += 1
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            success += 2
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            success += 1
    else:
        success += 0
    
#[1.1] if the project is completed
    if success >= adjCraftTime:
        out.append(f''' -title "Congrats! {name} has completed a(n) {item} using {tool}!" -f ":grey_exclamation: Crafting Complete | To add {item} to your inventory, you may add this to your Avrae bag using the !bag command, and you must add it to your equipment in Dndbeyond, if this effects character actions/spells you will want to run ``!update`` afterwards."''')
        #if the project is helped by another player, edit craftHelpers CVAR, take data needed for craftLog
        if projectList[pjCount].crafted == "helped":
            helperList  = load_json(get('craftHelpers','{"projects": [{"name":"","helper":[{"name":"","stat":["","",""]}]}]}')).projects
            hpCount     = len(helperList)
            for project in helperList:
                if project.name == item:
                    pjIndex     = helperList.index(project)
                    helpers     = ''
    #Get required helper info for craftLog    
                    for crafter in helperList[pjIndex].helper:
                        cont    = int(crafter.stat[0])+ int(crafter.stat[1])*2 - int(crafter.stat[2])
                        string  = '{"name": "'+ crafter.name +'","stat": "' + cont  + '"},'
                        helpers += string 
                    
                    delComma    = len(helpers)-1
                    helpers     = helpers[:delComma]
                    helper      = '"helper": [' + helpers + ']'  #this is for the craftLog
                    helperList.remove(project)
            
            if hpCount == 1:
                #it's the only one project that's helped in the list
                ch.delete_cvar("craftHelpers")
            else:
                #reconstruct craftProjects CVAR
                projects = ''
                for project in helperList:
                    helper    = "" + project.helper
                    string    = '{"name": "'+ project.name + '","helper":' + helper.replace("'", "^").replace('^','"') + '},'
                    projects += string
                                
                delComma    = len(projects)-1
                projects    = projects[:delComma]
                new         = '{"projects": [' + projects + ']}'
                
                ch.set_cvar("craftHelpers", new)
                
    #Get required info for craftLog if there's no helper       
        else:
            helper  = '"helper": [{"name": "n/a","stat": "n/a"}]'  #this is for the craftLog
            
    #reconstruct data for craftLog CVAR
        hFinish = (time()-anchorPts)/3600
        dayWork = (hFinish - int(projectList[pjCount].tStart))//24
        tFinish = (''+dayWork).split('.')[0]
        
        newLog  = '{"name": "'+projectList[pjCount].name+'","baseItem": "'+projectList[pjCount].name+'","resource": "'+projectList[pjCount].resource+'","total": "'+projectList[pjCount].total+'","crafted": "'+projectList[pjCount].crafted+'","tFinish": "'+tFinish+'", '+helper+ '}' 
        
        if craftLog[0].name == '':
            new     = '{"projects": [' + newLog + ']}'
        else:
            projects= ''
            for project in craftLog:
                helper   = "" + project.helper
                string   = '{"name": "'+project.name+'","baseItem": "'+project.name+'","resource": "'+project.resource+'","total": "'+project.total+'","crafted": "'+project.crafted+'","tFinish": "'+project.tFinish+'","helper": '+helper.replace("'", "^").replace('^','"')+ '},'
                projects += string
            
            new     = '{"projects": [' + projects + newLog + ']}'
        ch.set_cvar("craftLogs", new)
        
        #delete the current project and set project on the top of the list as active
        projectList.remove(projectList[pjCount])
        
        if len(projectList) == 0:
            delCvar  = True
            ch.delete_cvar("craftProjects")
        else:
            pjActive = '{"name": "'+ projectList[0].name + '","resource": "'+ projectList[0].resource + '","success": "'+ projectList[0].success + '","total": "'+ projectList[0].total + '","crafted": "'+ projectList[0].crafted + '","tStart": "'+ projectList[0].tStart + '","isActive": "True"},'
            for project in projectList:
                projects    = ''
                if project.name == projectList[0].name:
                    string      = ''
                    projects   += string
                else:
                    string      = '{"name": "'+ project.name + '","resource": "' + project.resource + '","success": "'+ project.success + '","total": "'+ project.total + '","crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                    projects   += string  
            new      = '{"projects": [' + pjActive + projects  + ']}'
          
#[1.2] if the project is not completed
    else:
        out.append(f''' -title "{name} continues to work on {item} using their {tool}." ''')
        
        projects    = ''
        for project in projectList:
            if project.name == item:
                string      = '{"name": "'+ project.name + '","resource": "' + project.resource + '","success": "'+ success + '","total": "'+ adjCraftTime + '","crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "True"},'
                projects   += string
            else:
                string      = '{"name": "'+ project.name + '","resource": "' + project.resource + '","success": "'+ project.success + '","total": "'+ project.total + '","crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                projects   += string        
        new      = '{"projects": [' + projects  + ']}'
    
    if delCvar == False:
        #delete a comma after last entry
        delComma = len(new)-3
        new      = new[:delComma] + new[-2:]
        ch.set_cvar("craftProjects", new)
    
   #OUTPUTS
    projectList = load_json(get('craftProjects','{"projects": [{"name":"","resource":"","success":"","total":"","crafted":"","tStart":"","isActive":""}]}')).projects
    pjList   = []
    for project in projectList:
        pjList.append(f"{project.name} <status: {project.success}/{project.total}> {'*(Active Project)*' if project.isActive == 'True' else ''}")
  
    pjDisp   = 'None\n*Create a new crafting project with `!craft -c \\"item name\\"`.*' if delCvar == True else " - "+"\n - ".join(pjList)
    pjStatus = f"{success}/{adjCraftTime}"
    out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**Tool check {attDisp}:** {check}\n{cStatus}\n**Crafting status:** {pjStatus}" -f ":scroll: Your current crafting projects:|{pjDisp}" -f "Realmsmith's Crafting Guide|In order to craft an item you will be able to make a single check per long rest to see if you are successful in crafting or not. Each day your character may make a Proficiency Check with the associated tools/kit. With a successful total roll of 12 or higher you succeed in crafting for that day. Heroes of the Realm and higher only require a successful total roll of 10 or higher. Rolling a Natural 20 counts for two successful days of crafting, whereas a Natural 1 results in an additional failed day above the one you rolled for." ''')
    if halfLuck:
        out.append(f''' -f "{hLuck}" ''')
    if reliableTalent:
        out.append(f''' -f "{rTalentDisp}" ''')
    if giftScribe:
        out.append(f''' -f "{giftedScribeDisp}" ''')
    if medIntuition:
        out.append(f''' -f "{mIntuitionDisp}" ''')
    if everHospit:
        out.append(f''' -f "{everHospitableDisp}" ''')
    if artBlessing:
        out.append(f''' -f "{artBlessingDisp}" ''')
    if foundry:
        out.append(f''' -f "{oDisp}" ''')
    if ftUse:
        out.append(f''' -f "{ftDisp}" ''')
        if ftActive:
            out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
        else:
            out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
    if dviUse:
        out.append(f''' -f "{dviDisp}" ''')
        if dviActive:
            out.append(f''' -f "{dvi} (-1)|{ch.cc_str(dvi)}" ''')
        else:
            out.append(f''' -f "{dvi}|{ch.cc_str(dvi)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''')
    return '\n'.join(out)    
        
#[2] CRAFT FOR SELF, IF PROJECT NOT EXISTS: create a new project
elif int(resHeld) >= int(resNeeded):
    #cc stuffs
    ch.mod_cc(munRes,-resNeeded,True)
    ch.mod_cc(cc,-1,True)
            
    #roll results
    if crit == 2:
        cStatus      = ":x: **Check status:** Critical Fail"
        adjCraftTime += 1
        success = 0
    elif check.total >= DC:
        if crit == 1:
            cStatus = ":white_check_mark: **Check status:** Critical Success!"
            success = 2
        else:
            cStatus = ":white_check_mark: **Check status:** Success"
            success = 1
    else:
        success = 0
    
#[2.1] if new project completed as the same day it's started, no need Rearrange CVAR
    if success >= adjCraftTime:
        out.append(f''' -title "Congrats! {name} has completed a(n) {item} using {tool}!" -f ":grey_exclamation: Crafting Complete|To use this/these {item} you must add them to your inventory, primarily you must add {item} to your equipment in Dndbeyond, and run ``!update`` in the [#rp-character-builder](https://discord.com/channels/673925841230626832/734510070062121090). Additionally, to add this item to your Avrae bag, run ``!bag 'bag name' + 'item name'`` to add this to a specified bag." ''') 

        
    #Dump into craftLog CVAR
        newLog  = '{"name": "'+ item +'","baseItem": "'+ item +'","resource": "'+ resNeeded +'","total": "'+ adjCraftTime +'","crafted":"'+ pjCraft +'","tFinish": "0","helper": [{"name": "n/a","stat": "n/a"}]}'
        if craftLog[0].name == '':
            new     = '{"projects": [' + newLog + ']}'
        else:
            projects= ''
            for project in craftLog:
                helper   = "" + project.helper
                string   = '{"name": "'+project.name+'", "baseItem": "'+project.baseItem+'" ,"resource": "'+project.resource+'","total": "'+project.total+'","crafted": "'+project.crafted+'","tFinish": "'+project.tFinish+'","helper": '+helper.replace("'", "^").replace('^','"')+ '},'
                projects += string
            
            new     = '{"projects": [' + projects + newLog + ']}'
        ch.set_cvar("craftLogs", new)

#[2.2] if new project still going    
    else:
        out.append(f''' -title "{name} works to craft {item} using their {tool}." ''')
        
        #create the project's CVAR
        pjCraft = "self"
        pjNew   = '{"name": "'+ item + '","resource": "'+ resNeeded+ '","success": "'+ success+ '","total": "'+ adjCraftTime + '","crafted": "'+ pjCraft + '","tStart": "'+ tStart + '","isActive": "True"},'
        
        if projectList[0].name =="":
            new = '{"projects": [' + pjNew + ']}'
        else:
            projects = ""
            for project in projectList:
                string = '{"name": "'+ project.name + '","resource": "' + project.resource + '","success": "'+ project.success + '","total": "'+ project.total + '","crafted": "'+ project.crafted + '","tStart": "'+ project.tStart + '","isActive": "False"},'
                projects += string
            new = '{"projects": [' + pjNew  + projects + ']}'
            
        #delete a comma afer last entry before set the CVAR    
        delComma = len(new)-3
        new      = new[:delComma] + new[-2:]
        ch.set_cvar("craftProjects", new)
    
   #OUTPUTS
    projectList = load_json(get('craftProjects','{"projects": [{"name":"","resource":"","success":"","total":"","crafted":"","tStart":"","isActive":""}]}')).projects
    pjList  = []
    for project in projectList:
        pjList.append(f"{project.name} <status: {project.success}/{project.total}> {'*(Active Project)*' if project.isActive == 'True' else ''}")
    pjDisp  = 'None\n*Create a new crafting project with `!craft -c \\"item name\\"`.*' if projectList[0].name =="" else " - "+"\n - ".join(pjList)
    pjStatus= f"{success}/{adjCraftTime}"
    out.append(f''' -desc "{ctmDisp}**Item name:** {item}\n**Tool check {attDisp}:** {check}\n{cStatus}\n**Crafting status:** {pjStatus}\n{rIndicator}**Mundane Resources held (-{resNeeded}):** {ch.cc_str(munRes)}" -f ":scroll: Your current crafting projects:|{pjDisp}" -f "Realmsmith's Crafting Guide|In order to craft an item you will be able to make a single check per long rest to see if you are successful in crafting or not. Each day your character may make a Proficiency Check with the associated tools/kit. With a successful total roll of 12 or higher you succeed in crafting for that day. Heroes of the Realm and higher only require a successful total roll of 10 or higher. Rolling a Natural 20 counts for two successful days of crafting, whereas a Natural 1 results in an additional failed day above the one you rolled for." ''')
    if giftScribe:
        out.append(f''' -f "{giftedScribeDisp}" ''')
    if medIntuition:
        out.append(f''' -f "{mIntuitionDisp}" ''')
    if everHospit:
        out.append(f''' -f "{everHospitableDisp}" ''')
    if artBlessing:
        out.append(f''' -f "{artBlessingDisp}" ''')
    if foundry:
        out.append(f''' -f "{oDisp}" ''')
    if ftUse:
        out.append(f''' -f "{ftDisp}" ''')
        if ftActive:
            out.append(f''' -f "{ft} (-1)|{ch.cc_str(ft)}" ''')
        else:
            out.append(f''' -f "{ft}|{ch.cc_str(ft)}" ''')
    if dviUse:
        out.append(f''' -f "{dviDisp}" ''')
        if dviActive:
            out.append(f''' -f "{dvi} (-1)|{ch.cc_str(dvi)}" ''')
        else:
            out.append(f''' -f "{dvi}|{ch.cc_str(dvi)}" ''')
    out.append(f''' -f "{cc} (-1)|{ch.cc_str(cc)}"  ''')
    return '\n'.join(out)
else:
    return f''' -title ":x: Error: Insufficient resource amounts!" -desc "You does not have enough resources to craft a(n) {item}; you need {resNeeded}{rIndicator} to do so, and you have {resHeld}{rIndicator} on your person." -f "{cc}|{ch.cc_str(cc)}" '''
    
</drac2>
-color <color>
-footer '!craft -c "item name" [-t @player]  | help'
