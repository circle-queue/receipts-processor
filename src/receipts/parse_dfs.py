import pandas as pd


def read_df():
    """
    Column a: The receipt text (sometimes including price)
    Column b: Sometimes the price

    Returns dataframe with
        MultiIndex[receipt_number: int, receipt_index: int]
        Columns[item: str, price: float]
    """
    df = pd.read_parquet("data.parquet").reset_index(names=["receipt_index"])
    num = df.receipt_index
    increasing = num == num.shift(1) + 1
    df["receipt_number"] = (~increasing).cumsum()
    df["b"] = df.b / 100
    df = df.query("receipt_number < 175")

    df = (
        df.set_index(["receipt_number", "receipt_index"])
        .pipe(correctly_split_price)
        .dropna(subset="b")  # No price: totals, card info etc.
        .query(
            "~a.str.contains('(?i)i alt|moms|total|byttepenge|køb|betal|dankort|debetkort|mastercard|kl\\.')"
        )
        .pipe(discard_unit_price)  # must be done before deduct rabat for correctness
        .pipe(deduct_rabat)
        .pipe(expand_repeat_purchases)
        .eval(
            "a = a.str.replace('(?i)([^ \w]|x.?tra|coop|cheasy|øko|änglemark|365|thise|xtra|extra|arla)', '', regex=True)"
        )
        .eval("a = a.str.strip()")
    )
    print(df.columns)
    df.columns = ["item", "price"]
    return df


def correctly_split_price(df):
    """Ensures the first column contains the item name: str, and second is cost: float"""
    split_cost = (
        df.a.str.extract("(.+?)(\d+[,.]\d+)(-?)$")
        .set_axis(["a", "b", "minus"], axis=1)
        .dropna()
        .eval("b = minus + b")  # put minus in front
        .eval("b = b.str.replace(',', '.')")  # correct delimiter
        .astype({"b": float})
        .drop(columns="minus")
    )
    df = df.copy()
    df.loc[split_cost.index] = split_cost
    return df


def discard_unit_price(df):
    """
    2 x HINDBÆR OG BLÅBÆR	3790.0
    á 18,95	NaN
    This means 2x18.95 should be eq to 37.90

    We dont use the á, so we discard these records
    """
    # Sanity check
    next_is_a = df.a.str.contains("á").shift(-1).fillna(False)
    x = df.a.str.contains("x")
    x_followed_by_a = x & next_is_a
    does_a_follow_x = (next_is_a == x_followed_by_a).all()
    assert does_a_follow_x  # '2 x Juice 20 dkk \n á 10 dkk each'
    # end sanity check
    return df[~df.a.str.contains("á")]


def expand_repeat_purchases(df):
    """Turns one "3 x ITEMNAME" -> 3 rows of "ITEMNAME", "ITEMNAME", "ITEMNAME"."""
    df_ = df.copy()
    units = df.a.str.extract("^(?:(\d+) ?x ?)?(.+)").fillna(1).astype({0: int})
    df_["units"] = units[0]
    df_["a"] = units[1]
    df_["b"] /= df_["units"]
    df_ = df_.loc[df.index.repeat(df_.units)]
    return df_.drop(columns="units")


def deduct_rabat(df):
    """Removes any discounts from the original item"""
    rabat_idx = df.a.str.contains("(?i)rabat") & ~df.a.str.contains("(?i)i alt")
    rabat = df[rabat_idx]

    rabat_items = rabat_idx.shift(-1).fillna(False)
    df.loc[rabat_items, "b"] += rabat.b.values
    return df[~rabat_idx]


def print_25_most_common():
    df = read_df()
    most_common_25 = df.item.value_counts().rename("counts").sort_values().tail(25)
    print(most_common_25)


if __name__ == "__main__":
    print_25_most_common()
