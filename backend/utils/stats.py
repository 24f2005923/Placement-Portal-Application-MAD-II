def create_stat_item(label, value, icon, tone):
    """
    Creates a standard formatted dashboard statistic item.
    """
    return {
        'label': label,
        'value': str(value),
        'icon': icon,
        'tone': tone
    }
