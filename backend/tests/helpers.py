def build_flat_xml(
    flat_id: str = "flat-1", status: str = "FREE", room: str = "2", area: str = "45.5"
) -> str:
    return f"""
        <flat>
            <flat_id>{flat_id}</flat_id>
            <status>{status}</status>
            <room>{room}</room>
            <floor>5</floor>
            <area>{area}</area>
            <price>10000000</price>
            <price_base>11000000</price_base>
        </flat>
    """


def build_feed_xml(
    *flats: str, name: str = "ЖК Тест", address: str = "г. Тест, ул. Тестовая, 1"
) -> bytes:
    flats_xml = "".join(flats) if flats else build_flat_xml()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed>
        <object>
            <name>{name}</name>
            <address>{address}</address>
            <buildings>
                <building>
                    <flats>
                        {flats_xml}
                    </flats>
                </building>
            </buildings>
        </object>
    </feed>
    """.encode("utf-8")
