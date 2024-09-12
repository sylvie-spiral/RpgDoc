multiline <drac2>
o,ms,ch,pa,args = [],[],character(),argparse("&*&"),&ARGS&
fields,delta,base = [],0,ch.coinpurse.total
showHelp = False

using(
    bagLib = '4119d62e-6a98-4153-bea9-0a99bb36da2c'
)

# svar for store:
storeSvarNameBase = f"store{ctx.channel.id}"
storeSvarNameCats = f"{storeSvarNameBase}Categories"
cats = get_svar(storeSvarNameCats)

inv = load_json(cats) if None != cats and len(cats) else []

if inv == None or len(inv) == 0:
  # if there is no inventory, tell people what to do
  ms.append(f"This channel or thread is not currently a store.")
  ms.append(f"If this is incorrect, inventory for this store needs to be set up in svar {storeSvarName}.")
  ms.append(f"Run in Category: {ctx.channel.category.id} / {ctx.channel.category.name}")
  ms.append(f"Run in Channel: {ctx.channel.id} / {ctx.channel.name}")
  ms.append(f"Topic: {ctx.channel.topic}")
else:
  y = 0

  # How many args do we have?
  if len(args) >= 1 and len(args) <= 2:
    amount = 1
    index = -1
    target = None
    it = []
    item = []

    if (len(args)) == 1:
        target = args[0]
    else:
       # first parameter should be a number
       amount = int(floor(args[0]))
       target = args[1]

    if target.isnumeric():
      index = int(target)
    else:               
      target = target.lower()

    for cat in inv:
      temp = (cat.split(' '))[0]
      data = get_svar(f"{storeSvarNameBase}{temp}").split('\n')
      
      for x in data:
        line = x.split('|')
        if (len(line) >= 4):
          y += 1
          name = line[0]
          price = float(line[1])
          count = int(line[3])

          if target.isnumeric() and y == index:
              item = line
              target = line[0]
              it.append(target)
              break
          else:               
              if name.lower() == target:
                it = []
                it.append(name)
                item = line
                break
              elif target in name.lower():
                item = line
                it.append(name)

    # it should now contain a single item
    if len(it) == 0:
        ms.append(f"I couldn't find {target} in the shop list for {ctx.channel.name}")
    elif len(it) > 1:      
        matches = ",".join(it)
        ms.append(f"The following items match {target}")
        ms.append(f"{matches}")
    else:
        if amount < 1:
            ms.append(f"You must buy a positive amount, seriously?")
        else:
            target = it[0]

            # purchase the item            
            ms.append(f"{ch.name} wants to purchase {amount} {target}")

            price = float(item[1])

            totPrice = price * amount
            if totPrice > base:
                ms.append(f"You need {totPrice}GP, but you only have {base}GP")
            else:
                # amount to move gold
                delta = 0 - totPrice

                # base amount
                count = int(item[3])

                # number of items to add
                count = count * amount

                cp = int(price * 100 * amount)

                # take the gold
                changes = ch.coinpurse.modify_coins(cp = -cp, autoconvert = True)

                changeText = []
                for y in changes:
                  if y != 'total':
                    changeText.append(f"{changes[y]:0.0f} {y}")
                  else:
                    changeText.append(f"({changes[y]:0.2f} {y})") 
                
                
                fields.append(f"'Changes|{' '.join(changeText)}'")

                # add the item
                bags = bagLib.load_bags(ch)
                bagname = f"{ctx.channel.name} Bag"
                bag = bagLib.get_bag(bags, bagname)
                if bag == None:
                    bag = bagLib.new_bag(bags, bagname)

                bagLib.modify_item(bags, item = target, quantity = count, bag_name = bagname)
                bagLib.save_bags(bags, ch = ch)

                ms.append(f"Added {target} to {bagname} ({count})")
        
  else:
     showHelp = True

  coins = ch.coinpurse.get_coins()
  fields.append(f""" "Coinpurse|{coins.pp} PP, {coins.gp} GP, {coins.ep} EP, {coins.sp} SP, {coins.cp} CP" """)
  
if showHelp:
    ms.append(f"Usage:")
    ms.append(f"`!buy <id>` - buy one item with the specified ID (`!buy 1`)")
    ms.append(f"`!buy <quantity> <id>` - buy several items with the same ID (`!buy 20 1`)")
    ms.append(f"`!buy <name>` - buy one item by name (`!buy 'Healing Potion'`)")
    ms.append(f"`!buy <quantity> <name>` - buy many items by name (`!buy 20 'Healing Potion'`)")
    ms.append("Use `!catalog` to see what is for sale.")
  
dt = "\n".join(ms)
o.append(f'''!embed -desc "{dt}" -footer "!buy <item> | !buy <amt> <item>"  -f {" -f ".join(fields)} -title "{ch.name}"''')

return "\n".join(o)
</drac2>