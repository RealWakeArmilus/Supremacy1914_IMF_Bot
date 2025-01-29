from matplotlib import pyplot as plt


async def create_chart_currency_capitals_from_country(number_match: str, from_name_country: str, data_currency_capitals: list) -> str:
    """
    Создание круглой диаграммы капитала валют конкретного государства
    
    :param number_match: номер матча
    :param from_name_country: название государства для которого делается диаграмма
    :param data_currency_capitals: данные капитала данного государства
    :return: name_chart : str
    """
    labels = []
    amount = []

    for currency_capital in data_currency_capitals:
        labels.append(f'{currency_capital['currency_tick']}')
        amount.append(f'{currency_capital['amount']}')

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.pie(
        amount,
        labels=labels,
        autopct='%1.1f%%',
        wedgeprops=dict(width=0.3),
        startangle=90
    )

    watermark = (
        'Telegram Bot:\n'
        '@Supremacy1914_IMF_Bot\n\n'
        f'{from_name_country}\n'
        f'№ матча: {number_match}'
    )

    plt.text(
        0, 0,  # Координаты (x, y) относительно графика
        watermark,  # Ваш текст
        fontsize=16,  # Размер шрифта
        color='white',  # Цвет текста
        ha='center',  # Выравнивание по горизонтали (центрировано)
        va='center',  # Выравнивание по вертикали
        bbox=dict(facecolor='black', alpha=0.8, edgecolor='white', boxstyle='round,pad=2')  # Оформление фона
    )

    ax.axis('equal')
    plt.tight_layout()

    name_chart = f'chart/{number_match}_{from_name_country}.png'

    plt.savefig(name_chart)

    return name_chart


    # cmap = plt.cm.get_cmap()  # Можно заменить на Set3, Paired и т.д.
    # colors = [cmap(i / len(data_currency_capitals)) for i in range(len(data_currency_capitals))]
    #
    # fig, ax = plt.subplots()
    # ax.pie(amount, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    #
    # ax.axis('equal')
    #
    # # Сохранение диаграммы
    # plt.savefig('chart.png')