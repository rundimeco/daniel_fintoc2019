import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn2

grp1 = set(['cheese-a', 'cheese-b', 'cheese-c', 'cheese-d',
            'cheese-e', 'cheese-f', 'cheese-g', 'cheese-h',
            'cheese-i', 'cheese', 'red wine'])
grp2 = set(['red wine-a', 'red wine-b', 'red wine-c', 'red wine-d',
            'red wine-e', 'red wine-f', 'red wine-g', 'red wine-h',
            'red wine-i', 'red wine-j', 'red wine-k', 'red wine-l',
            'red wine', 'cheese'])

v2 = venn2([grp1, grp2], set_labels = ('grp1', 'grp2', 'grp3'))

v2.get_patch_by_id('10').set_color('yellow')
v2.get_patch_by_id('01').set_color('red')
v2.get_patch_by_id('11').set_color('orange')

v2.get_patch_by_id('10').set_edgecolor('none')
v2.get_patch_by_id('01').set_edgecolor('none')
v2.get_patch_by_id('11').set_edgecolor('none')

v2.get_label_by_id('10').set_text('Only cheese\n(36%)')
v2.get_label_by_id('01').set_text('Only red wine\n(48%)')
v2.get_label_by_id('11').set_text('Both\n(16%)')

plt.show()