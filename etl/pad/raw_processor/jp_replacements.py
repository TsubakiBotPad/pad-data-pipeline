# A list of JP to EN replacement strings for dungeon/subdungeon names.
_JP_EN_CHUNKS = {
    'ノーコン': 'No Continues',
    '回復なし': 'No RCV',
    '覚醒無効': 'Awoken Skills Invalid',
    '5×4マス': '5x4 Board',
    '7×6マス': '7x6 Board',
    '全属性必須': 'All Att. Req.',
    '覚醒スキル無効': 'Awoken Skills Invalid',
    '特殊': 'Special',
    '同キャラ禁止': 'No Dupes',
    'スキル使用不可': 'Skills Invalid',
    'アシスト無効': 'Assists Invalid',
    'リーダースキル無効': 'Leader Skills Invalid',
    '落ちコンなし': 'No Skyfall Combos',
    '★6以下のみ': '★6 or lower',
    '固定チーム': 'Fixed Team',
    '金曜': 'Mythical',
    '木曜': 'Mythical',
    '水曜': 'Legend',
    '火曜': 'Mythical',
    '3色限定': 'Tricolor',
    '4体以下編成': 'Teams of 4 or less',
    '土日': 'Legend',
    '月曜': 'Legend',
    'HP10固定': '10 HP',
    '3体以下編成': 'Teams of 3 or less',
    '2体以下編成': 'Teams of 2 or less',
    'HP100万固定': '1.000.000 HP',
    'LS無効': 'L. Skills Invalid',
    '操作時間': 'Orb move time ',
    '秒固定': ' sec',
    '制限時間': 'Time limit ',
    '分': ' mins',
    '日曜': 'Legend',
    '土曜': 'Annihilation',
    'リーダー助っ人固定': 'Fixed helper'
}


# Finds JP style brackets in a name, and replaces chunks against a list of known translations.
def jp_en_replacements(name: str):
    if not ('【' in name and '】' in name):
        return name

    # Extract the JP inner part of the brackets
    part = name[name.index('【') + 1:name.index('】')]
    final_part = part

    # Replace JP bits piece by piece
    for k, v in _JP_EN_CHUNKS.items():
        final_part = final_part.replace(k, v)

    # Swap out any bits we could translate
    return name.replace(part, final_part)
