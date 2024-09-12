multiline
<drac2>
o,ms,ch,pa,args = [],[],character(),argparse("&*&"),&ARGS&

# svar for store:
storeSvarNameBase = f"store{ctx.channel.id}"
storeSvarNameCats = f"{storeSvarNameBase}Categories"
cats = get_svar(storeSvarNameCats)

inv = load_json(cats) if None != cats and len(cats) else []

if inv == None or len(inv) == 0:
  # if there is no inventory, tell people what to do
  ms.append(f"This channel or thread is not currently a store.")
  ms.append(f"If this is incorrect, inventory for this store needs to be set up in svar {storeSvarNameBase}Categories, etc.")
  ms.append(f"Run in Category: {ctx.channel.category.id} / {ctx.channel.category.name}")
  ms.append(f"Run in Channel: {ctx.channel.id} / {ctx.channel.name}")
  ms.append(f"Topic: {ctx.channel.topic}")
else:
  y = 0
  match = args[0].lower() if len(args) > 0 else ''
      
  for cat in inv:
    ms = []
    ms.append(f"The following items are available at {ctx.channel.name}:")
    ms.append(f'**{cat}**')
    ms.append('```')
    ms.append('ID |GP     |NAME')
    ms.append('===+=======+======================================')

    temp = (cat.split(' '))[0]

    data = get_svar(f"{storeSvarNameBase}{temp}").split('\n')
    
    for x in data:
      line = x.split('|')
      if (len(line) >= 4):
        y += 1
        name = line[0]
        price = float(line[1])
        catOnItem = line[2]
        count = int(line[3])
        desc = ''

        if (len(line) >= 5):
          desc = line[4]
        
        if (match == '') or (match in cat.lower()) or (match in name.lower()) or (match in catOnItem.lower()):
          ms.append(f'{y:03}|{price:>7.2f}|{name}{f" ({count})" if count > 1 else ""}')
          if len(desc) > 0:
            ms.append(f' - {desc}\n')
  
    ms.append('```')
    ms.append("To purchase an item, type `!buy <id>` or `!buy <item name>`. To purchase several items, type `!buy <quantity> <id>` or `!buy <quantity> 'Item Name'`")
    dt = "\n".join(ms)
    o.append(f'''!embed -desc "{dt}" -footer !catalog ''')

return "\n".join(o)
</drac2>