import sqlite3
from parser import parse_multiple_invoices

DB_NAME = "ocr_master.db"
TABLE_NAME = "ocr_line_items" # Ensure this matches your table_creation.py


def insert_extracted_data():
    con = None
    insert_count = 0

    try:
        # Connect to database
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        # Get parsed bill data
        all_bill_data = parse_multiple_invoices()

        if not all_bill_data:
            print("no data")
            return

        print(f"data to be extracted, {len(all_bill_data)}")

        # Loop through each bill
        for bill_dict in all_bill_data:
            invoice_no = bill_dict.get("Invoice_No")
            issue_date = bill_dict.get("Issue_Date")
            billed_to = bill_dict.get("billed_to")
            billed_by = bill_dict.get("billed_by")
            grand_total = bill_dict.get("Grand_Total")
            source_file = bill_dict.get("source_file")

            line_items = bill_dict.get("line_items", [])

            if not line_items:
                print(f"Skipping invoice {invoice_no}: no line items to insert.")
                continue

            # Insert one row per line item
            for line_id, item in enumerate(line_items, start=1):
                desc = item.get('service_description')
                amt = item.get('Amount')
                category = item.get('Category')
                try:
                    cur.execute(
                        f"""
                        INSERT OR REPLACE INTO {TABLE_NAME}
                        (
                            Invoice_No,
                            line_item_id,
                            Issue_Date,
                            billed_to,
                            billed_by,
                            Description,
                            Category,
                            Amount,
                            Grand_Total,
                            source_file
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            invoice_no,
                            line_id,
                            issue_date,
                            billed_to,
                            billed_by,
                            desc,
                            category,
                            amt,
                            grand_total,
                            source_file,
                        ),
                    )
                    insert_count += 1

                except sqlite3.IntegrityError as e:
                    print(
                        f"Duplicate skipped: Invoice {invoice_no}, "
                        f"line_item_id {line_id} → {e}"
                    )

        con.commit()
        print(f"data insertion for {insert_count} completed")

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")

    except Exception as e:
        print(f"General Error during insertion: {e}")

    finally:
        if con:
            con.close()

def insert_single_bill_data(bill_dict: dict) -> int:
    """
    Inserts a single structured bill dictionary into the database.
    Returns the number of line items inserted.
    """
    con = None
    insert_count = 0

    try:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        invoice_no = bill_dict.get("Invoice_No")
        issue_date = bill_dict.get("Issue_Date")
        billed_to = bill_dict.get("billed_to")
        billed_by = bill_dict.get("billed_by")
        grand_total = bill_dict.get("Grand_Total")
        source_file = bill_dict.get("source_file")
        line_items = bill_dict.get("line_items", [])

        if not line_items:
            print(f"Skipping invoice {invoice_no}: no line items to insert.")
            return 0

        for line_id, item in enumerate(line_items, start=1):
            desc = item.get('service_description')
            amt = item.get('Amount')
            category = item.get('Category')

            try:
                cur.execute(
                    f"""
                    INSERT OR REPLACE INTO {TABLE_NAME}
                    (
                        Invoice_No,
                        line_item_id,
                        Issue_Date,
                        billed_to,
                        billed_by,
                        Description,
                        Category,
                        Amount,
                        Grand_Total,
                        source_file
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        invoice_no,
                        line_id,
                        issue_date,
                        billed_to,
                        billed_by,
                        desc,
                        category,
                        amt,
                        grand_total,
                        source_file,
                    ),
                )
                insert_count += 1
            except sqlite3.IntegrityError as e:
                print(
                    f"Duplicate skipped: Invoice {invoice_no}, "
                    f"line_item_id {line_id} → {e}"
                )

        con.commit()
        print(f"Inserted {insert_count} line items for invoice {invoice_no}.")
        return insert_count

    except sqlite3.Error as e:
        print(f"SQLite Error during single bill insertion: {e}")
        return 0
    except Exception as e:
        print(f"General Error during single bill insertion: {e}")
        return 0
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    insert_extracted_data()
