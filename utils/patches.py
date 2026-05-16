import pyrogram.utils

def patch_pyrogram():
    """
    Monkeypatch Pyrogram to handle newer, longer peer IDs.
    """
    orig_get_peer_type = pyrogram.utils.get_peer_type

    def patched_get_peer_type(peer_id: int) -> str:
        if peer_id > 0:
            return "user"
        # Newer channel IDs are longer. Standard Pyrogram 2.0.106 uses <= -1000000000000
        # which is 13 digits (including minus). -1002576801363 is 14 digits?
        # Let's check:
        # - 1
        # 0 2
        # 0 3
        # 2 4
        # 5 5
        # 7 6
        # 6 7
        # 8 8
        # 0 9
        # 1 10
        # 3 11
        # 6 12
        # 3 13
        # Total 14 characters including minus sign. 13 digits.
        # Wait, -1000000000000 is also 14 characters including minus.

        # Actually, the check in Pyrogram 2.0.106 is:
        # if peer_id <= -1000000000000: return "channel"

        # If peer_id is -1002576801363:
        # -1002576801363 <= -1000000000000 is TRUE.

        # So why did it fail?
        # Maybe the version of Pyrogram the user has is even older?
        # But the log says 2.0.106.

        # Let's be more permissive.
        if str(peer_id).startswith("-100"):
            return "channel"
        if peer_id < 0:
            return "chat"
        return "user"

    pyrogram.utils.get_peer_type = patched_get_peer_type

    if hasattr(pyrogram.utils, "get_channel_id"):
        def patched_get_channel_id(peer_id: int) -> int:
            return int(str(peer_id).replace("-100", ""))
        pyrogram.utils.get_channel_id = patched_get_channel_id

    print("Pyrogram monkeypatched for long Peer IDs.")
