import pandas as pd

df = pd.read_csv('input.csv')

df['url_bis'] = ''

if (df['links'].iloc[281] == 'https://youtu.be/cwqJOl3yan8?t=3292' and df['id'].iloc[281] == 'fe926979bb765dc79482e1da3b0a9b89'):
    df['url_bis'].iloc[281] = 'https://www.youtube.com/watch?v=cwqJOl3yan8&t=3292s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[285] == 'https://youtu.be/ERqxZMgKExM?t=947' and df['id'].iloc[285] == '07dd0de207df9fa42d2e7e10de86519a'):
    df['url_bis'].iloc[285] = 'https://www.youtube.com/watch?v=ERqxZMgKExM&t=947s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[587] == 'https://youtu.be/w68994lQMgA?t=839' and df['id'].iloc[587] == 'c2ad49fba1415a33a829ea1b7adb6cef'):
    df['url_bis'].iloc[587] = 'https://www.youtube.com/watch?v=w68994lQMgA&t=839s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[594] == 'https://youtu.be/cwqJOl3yan8?t=3743' and df['id'].iloc[594] == '09b8a4269a6f48ccb097ce035a9ca694'):
    df['url_bis'].iloc[594] = 'https://www.youtube.com/watch?v=cwqJOl3yan8&t=3743s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[650] == 'https://youtu.be/xqqLVXSSGuo?t=1824' and df['id'].iloc[650] == '64d8dc3a371f3d6532f1a4c1db616adc'):
    df['url_bis'].iloc[650] = 'https://www.youtube.com/watch?v=xqqLVXSSGuo&t=1824s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[662] == 'https://youtu.be/xqqLVXSSGuo?t=1639' and df['id'].iloc[662] == 'ca406da0390226b1f8fee1bd3cd17eb9'):
    df['url_bis'].iloc[662] = 'https://www.youtube.com/watch?v=xqqLVXSSGuo&t=1639s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[669] == 'https://youtu.be/xqqLVXSSGuo?t=1716' and df['id'].iloc[669] == 'a093c53d911dc439236ad6e0a932acec'):
    df['url_bis'].iloc[669] = 'https://www.youtube.com/watch?v=xqqLVXSSGuo&t=1716s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[670] == 'https://youtu.be/-w-aYVXcOk4?t=6370' and df['id'].iloc[670] == '348cd4ce5f6656b090786f738d3f047c'):
    df['url_bis'].iloc[670] = 'https://www.youtube.com/watch?v=-w-aYVXcOk4&t=6370s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[671] == 'https://youtu.be/xqqLVXSSGuo?t=1318' and df['id'].iloc[671] == '9d9e66619c15f877761d5b0364a93fce'):
    df['url_bis'].iloc[671] = 'https://www.youtube.com/watch?v=xqqLVXSSGuo&t=1318s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[672] == 'https://youtu.be/xqqLVXSSGuo?t=1753' and df['id'].iloc[672] == '1c0ef4cf779bee1c71b0b4009a10003b'):
    df['url_bis'].iloc[672] = 'https://www.youtube.com/watch?v=xqqLVXSSGuo&t=1753s'
    print("ok url")
else:
    print("c'est mort")

if (df['links'].iloc[676] == 'https://youtu.be/cwqJOl3yan8' and df['id'].iloc[676] == 'b9eff082125c6eaaa6e9082b970fd635'):
    df['url_bis'].iloc[676] = 'https://www.youtube.com/watch?v=cwqJOl3yan8&t=3292s'
    print("ok url")
else:
    print("c'est mort")

df.to_csv("youtu.be_corriged.csv", index=False)
