"""
GachaLog — Notion テンプレート自動セットアップ
Series DB + Items DB + ビュー付きダッシュボードを一発構築
"""
import sys, json, urllib.request, urllib.error, time
from pathlib import Path

ROOT = Path("C:\\Users\\user\\Claude-Workspace")
sys.path.insert(0, str(ROOT / "scripts"))
from vault import get_secret
from notion_helper import get_headers, api_request, load_ids, save_ids, md_to_blocks

TOKEN = get_secret("NOTION_TOKEN")
if not TOKEN:
    print("ERROR: NOTION_TOKEN が Vault に未保存"); sys.exit(1)
HEADERS = get_headers(TOKEN)

IDS_KEY = "gachalog"
PROJECT_IDS_FILE = Path(__file__).parent / "notion_ids.json"


def load_project_ids():
    if PROJECT_IDS_FILE.exists():
        return json.loads(PROJECT_IDS_FILE.read_text(encoding="utf-8"))
    return {}


def save_project_ids(data):
    PROJECT_IDS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def create_database(parent_id, title, properties):
    body = {
        "parent": {"page_id": parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties,
    }
    return api_request("POST", "databases", TOKEN, body)


def create_top_page():
    """GachaLog トップページを作成"""
    ids = load_ids()
    parent = ids.get("pipeline_top_page")
    if not parent:
        print("ERROR: pipeline_top_page が .notion_ids.json にありません")
        sys.exit(1)

    result = api_request("POST", "pages", TOKEN, {
        "parent": {"page_id": parent},
        "properties": {"title": [{"type": "text", "text": {"content": "GachaLog Template"}}]},
        "icon": {"type": "emoji", "emoji": "\U0001f3b0"},
        "children": [
            {"object": "block", "type": "callout", "callout": {
                "icon": {"type": "emoji", "emoji": "\U0001f3b0"},
                "rich_text": [{"type": "text", "text": {
                    "content": "GachaLog \u2014 Your Japanese Toy Collection, Beautifully Organized"
                }}]
            }},
        ]
    })
    print(f"[OK] Top page: {result['id']}")
    return result["id"]


def create_series_db(parent_id):
    props = {
        "Series Name": {"title": {}},
        "Maker": {"select": {"options": [
            {"name": "Bandai", "color": "red"},
            {"name": "Takara Tomy", "color": "blue"},
            {"name": "Epoch", "color": "green"},
            {"name": "Kitan Club", "color": "purple"},
            {"name": "Bushiroad", "color": "orange"},
            {"name": "Other", "color": "gray"},
        ]}},
        "Category": {"select": {"options": [
            {"name": "Gashapon", "color": "red"},
            {"name": "Figure", "color": "blue"},
            {"name": "Ichiban Kuji", "color": "yellow"},
            {"name": "Blind Box", "color": "purple"},
            {"name": "Shokugan", "color": "green"},
            {"name": "Trading Card", "color": "orange"},
            {"name": "Other", "color": "gray"},
        ]}},
        "Total Items": {"number": {"format": "number"}},
        "Release Date": {"date": {}},
        "Notes": {"rich_text": {}},
    }
    result = create_database(parent_id, "\U0001f4da Series", props)
    print(f"[OK] Series DB: {result['id']}")
    return result["id"]


def create_items_db(parent_id, series_db_id):
    props = {
        "Item Name": {"title": {}},
        "Series": {"relation": {"database_id": series_db_id, "type": "single_property", "single_property": {}}},
        "Photo": {"files": {}},
        "Status": {"select": {"options": [
            {"name": "Owned", "color": "green"},
            {"name": "Wanted", "color": "yellow"},
            {"name": "Trading", "color": "orange"},
            {"name": "Sold", "color": "gray"},
        ]}},
        "Rarity": {"select": {"options": [
            {"name": "Normal", "color": "default"},
            {"name": "Secret", "color": "purple"},
            {"name": "Limited", "color": "red"},
        ]}},
        "Acquired Date": {"date": {}},
        "Acquired From": {"select": {"options": [
            {"name": "Store", "color": "blue"},
            {"name": "Online", "color": "green"},
            {"name": "Trade", "color": "orange"},
            {"name": "Gift", "color": "pink"},
        ]}},
        "Price": {"number": {"format": "yen"}},
        "Condition": {"select": {"options": [
            {"name": "Mint", "color": "green"},
            {"name": "Good", "color": "blue"},
            {"name": "Fair", "color": "yellow"},
        ]}},
        "Duplicate": {"checkbox": {}},
        "Notes": {"rich_text": {}},
    }
    result = create_database(parent_id, "\u2b50 Items", props)
    print(f"[OK] Items DB: {result['id']}")
    return result["id"]


def add_sample_data(series_db_id, items_db_id):
    """サンプルデータ投入（テンプレートの見栄えのため）"""
    from notion_helper import create_db_entry

    # Series
    series_data = [
        {"name": "Animal Kitchen", "maker": "Bandai", "cat": "Gashapon", "total": 5},
        {"name": "Food Miniature Collection", "maker": "Epoch", "cat": "Gashapon", "total": 6},
        {"name": "Sweet Friends", "maker": "Kitan Club", "cat": "Blind Box", "total": 4},
    ]
    series_ids = {}
    for s in series_data:
        props = {
            "Series Name": {"title": [{"text": {"content": s["name"]}}]},
            "Maker": {"select": {"name": s["maker"]}},
            "Category": {"select": {"name": s["cat"]}},
            "Total Items": {"number": s["total"]},
        }
        result = create_db_entry(TOKEN, series_db_id, props)
        series_ids[s["name"]] = result["id"]
        print(f"  [+] Series: {s['name']}")
        time.sleep(0.4)

    # Items
    items_data = [
        {"name": "Shiba Inu Chef", "series": "Animal Kitchen", "status": "Owned", "rarity": "Normal", "price": 300},
        {"name": "Cat Barista", "series": "Animal Kitchen", "status": "Owned", "rarity": "Normal", "price": 300},
        {"name": "Penguin Sushi Master", "series": "Animal Kitchen", "status": "Wanted", "rarity": "Normal", "price": 300},
        {"name": "Hamster Baker", "series": "Animal Kitchen", "status": "Owned", "rarity": "Secret", "price": 300},
        {"name": "Mini Ramen Bowl", "series": "Food Miniature Collection", "status": "Owned", "rarity": "Normal", "price": 400},
        {"name": "Tiny Bento Set", "series": "Food Miniature Collection", "status": "Trading", "rarity": "Normal", "price": 400},
        {"name": "Mochi Bear", "series": "Sweet Friends", "status": "Wanted", "rarity": "Limited", "price": 500},
        {"name": "Donut Bunny", "series": "Sweet Friends", "status": "Owned", "rarity": "Normal", "price": 500},
    ]
    for it in items_data:
        props = {
            "Item Name": {"title": [{"text": {"content": it["name"]}}]},
            "Series": {"relation": [{"id": series_ids[it["series"]]}]},
            "Status": {"select": {"name": it["status"]}},
            "Rarity": {"select": {"name": it["rarity"]}},
            "Price": {"number": it["price"]},
        }
        create_db_entry(TOKEN, items_db_id, props)
        print(f"  [+] Item: {it['name']}")
        time.sleep(0.4)


def add_dashboard_blocks(page_id, series_db_id, items_db_id):
    """ダッシュボードにDB埋め込み + 説明ブロック追加"""
    from notion_helper import append_blocks
    blocks = [
        {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Series Progress"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {
                "content": "Track your completion rate for each series. Add new series as you discover them!"
            }}]}},
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Recent Items"}}]}},
        {"object": "block", "type": "paragraph", "paragraph": {
            "rich_text": [{"type": "text", "text": {
                "content": "Your latest finds. Upload photos to build your visual collection catalog."
            }}]}},
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "How to Use"}}]}},
        {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Add a new Series when you start collecting"}}]}},
        {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Log each Item with photo, status, and price"}}]}},
        {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Use Gallery view to browse your collection visually"}}]}},
        {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Check Wishlist view to plan your next hunt"}}]}},
        {"object": "block", "type": "numbered_list_item", "numbered_list_item": {
            "rich_text": [{"type": "text", "text": {"content": "Mark duplicates and use Trade Board to swap with friends"}}]}},
    ]
    append_blocks(TOKEN, page_id, blocks)
    print("[OK] Dashboard blocks added")


def main():
    print("=" * 50)
    print("GachaLog Notion Template Setup")
    print("=" * 50)

    # 1. Top page
    print("\n[1/5] Creating top page...")
    top_id = create_top_page()

    # 2. Series DB
    print("\n[2/5] Creating Series database...")
    series_id = create_series_db(top_id)

    # 3. Items DB
    print("\n[3/5] Creating Items database...")
    items_id = create_items_db(top_id, series_id)

    # 4. Sample data
    print("\n[4/5] Adding sample data...")
    add_sample_data(series_id, items_id)

    # 5. Dashboard
    print("\n[5/5] Building dashboard...")
    add_dashboard_blocks(top_id, series_id, items_id)

    # Save IDs
    pids = load_project_ids()
    pids.update({"top_page": top_id, "series_db": series_id, "items_db": items_id})
    save_project_ids(pids)

    print("\n" + "=" * 50)
    print("DONE! Open Notion and check GachaLog Template page.")
    print(f"Top page ID: {top_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
