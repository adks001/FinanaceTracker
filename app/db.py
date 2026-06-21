import logging
from supabase import create_client, Client
from app.config import SUPABASE_URL, SUPABASE_KEY
from app.categories import GLOBAL_CATEGORIES

logger = logging.getLogger(__name__)

# Initialize Supabase client
# If configuration is missing, we allow it to be None and validate at startup in ui.py
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}")

def init_supabase_client(url: str, key: str) -> bool:
    """Dynamically initializes or overrides the Supabase client."""
    global supabase
    try:
        supabase = create_client(url, key)
        return True
    except Exception as e:
        logger.error(f"Dynamic Supabase initialization failed: {e}")
        return False

def verify_connection() -> bool:
    """Verifies that the Supabase client is connected and working."""
    if not supabase:
        return False
    try:
        # Perform a simple select on categories
        supabase.table("categories").select("id").limit(1).execute()
        return True
    except Exception as e:
        err_msg = str(e)
        if "JWT expired" in err_msg or "PGRST303" in err_msg:
            logger.info("Supabase session JWT expired. Clearing session...")
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            return True
        logger.error(f"Supabase connection verification failed: {e}")
        return False

def seed_global_categories():
    """
    Seeds global categories in the database if they don't already exist.
    Checks and seeds missing ones dynamically.
    """
    if not supabase:
        return
    try:
        # Fetch existing global categories
        response = supabase.table("categories").select("name").is_("profile_id", "null").execute()
        existing_names = {cat["name"].lower() for cat in (response.data or [])}
        
        seed_data = []
        for name, info in GLOBAL_CATEGORIES.items():
            if name.lower() not in existing_names:
                seed_data.append({
                    "profile_id": None,
                    "name": name,
                    "svg_icon": info["svg"]
                })
        
        if seed_data:
            supabase.table("categories").insert(seed_data).execute()
            logger.info(f"Successfully seeded {len(seed_data)} missing global categories.")
    except Exception as e:
        logger.error(f"Failed to seed global categories: {e}")

# Profile Helpers
def get_profile(user_id: str) -> dict:
    """Fetches user profile by user UUID."""
    if not supabase:
        return {}
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
    return {}

def create_profile_if_not_exists(user_id: str, email: str, full_name: str = None, phone_no: str = None) -> dict:
    """
    Fall-back helper to ensure a user profile exists in public.profiles.
    Normally handled by database trigger, but this provides double security.
    """
    if not supabase:
        return {}
    try:
        profile = get_profile(user_id)
        if profile:
            return profile
        
        # Profile doesn't exist, insert manually
        insert_data = {
            "id": user_id,
            "email": email,
            "full_name": full_name or email.split("@")[0],
        }
        if phone_no:
            insert_data["phone_no"] = phone_no
            
        response = supabase.table("profiles").insert(insert_data).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
    return {}

# Category Helpers
def get_categories(user_id: str) -> list:
    """Fetches global categories AND user custom categories."""
    if not supabase:
        return []
    try:
        # Get global categories or user categories
        response = supabase.table("categories").select("*").or_(
            f"profile_id.is.null,profile_id.eq.{user_id}"
        ).order("name").execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return []

# Expense Helpers
def check_duplicate_expense(user_id: str, date: str, amount: float, merchant: str) -> list:
    """
    Checks if a matching expense (same date, amount, and case-insensitive merchant name)
    already exists for the user. Returns a list of duplicates if found.
    """
    if not supabase:
        return []
    try:
        response = supabase.table("expenses").select("*, categories(name)").eq("profile_id", user_id).eq("date", date).eq("amount", amount).execute()
        duplicates = []
        for exp in (response.data or []):
            if exp["merchant"].strip().lower() == merchant.strip().lower():
                duplicates.append(exp)
        return duplicates
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return []

def insert_expense(expense_data: dict) -> dict:
    """
    Inserts an expense record.
    If database returns a unique constraint error on raw_email_uid, returns None (duplicate caught).
    """
    if not supabase:
        raise RuntimeError("Supabase client is not connected.")
    try:
        response = supabase.table("expenses").insert(expense_data).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        # Check if it is a unique constraint error for raw_email_uid (Postgrest code 23505)
        err_msg = str(e)
        if "23505" in err_msg or "duplicate key value" in err_msg.lower():
            logger.info(f"Duplicate email alert ignored: raw_email_uid={expense_data.get('raw_email_uid')}")
            return None
        raise e
    return {}

def get_expenses(user_id: str) -> list:
    """Fetches all expense records for a user with category names joined."""
    if not supabase:
        return []
    try:
        response = supabase.table("expenses").select(
            "*, categories(name, svg_icon)"
        ).eq("profile_id", user_id).order("date", desc=True).execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return []

def delete_expense(expense_id: str, user_id: str) -> bool:
    """Deletes an expense. Secured by user_id check."""
    if not supabase:
        return False
    try:
        response = supabase.table("expenses").delete().eq("id", expense_id).eq("profile_id", user_id).execute()
        return len(response.data or []) > 0
    except Exception as e:
        logger.error(f"Error deleting expense: {e}")
        return False

def process_recurring_schedules(user_id: str):
    """
    Checks for any recurring templates (is_recurring = True) and generates 
    new expense instances for any due dates in the past/today.
    """
    if not supabase:
        return
    try:
        from datetime import datetime, date, timedelta
        today = date.today()
        
        # Get all templates for user
        res = supabase.table("expenses").select("*").eq("profile_id", user_id).eq("is_recurring", True).execute()
        templates = res.data or []
        
        def add_months(sourcedate, months):
            month = sourcedate.month - 1 + months
            year = sourcedate.year + month // 12
            month = month % 12 + 1
            day = min(sourcedate.day, [31,
                29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
            return date(year, month, day)

        def add_years(sourcedate, years):
            try:
                return date(sourcedate.year + years, sourcedate.month, sourcedate.day)
            except ValueError:
                return date(sourcedate.year + years, sourcedate.month, 28)

        for temp in templates:
            interval = temp.get("recurring_interval")
            if not interval or interval == "None":
                continue
                
            # Start date of cycle
            start_date_str = temp.get("date")
            last_run_str = temp.get("last_recurring_run")
            
            base_date = datetime.strptime(last_run_str or start_date_str, "%Y-%m-%d").date()
            
            # Find next due dates
            current_due = base_date
            generated_any = False
            
            while True:
                # Calculate next due date
                if interval == "Weekly":
                    next_due = current_due + timedelta(days=7)
                elif interval == "Monthly":
                    next_due = add_months(current_due, 1)
                elif interval == "Yearly":
                    next_due = add_years(current_due, 1)
                else:
                    break
                    
                if next_due > today:
                    break
                    
                # Create a new expense entry for this due date
                new_desc = temp.get("description") or ""
                cycle_note = f" (Recurring: {interval})"
                if cycle_note not in new_desc:
                    new_desc = (new_desc + cycle_note).strip()
                    
                new_expense = {
                    "profile_id": user_id,
                    "date": next_due.strftime("%Y-%m-%d"),
                    "merchant": temp["merchant"],
                    "description": new_desc,
                    "amount": float(temp["amount"]),
                    "earning_vs_expense": temp["earning_vs_expense"],
                    "category_id": temp["category_id"],
                    "is_shared": temp["is_shared"],
                    "split_percentage": float(temp["split_percentage"]),
                    "shared_person_name": temp.get("shared_person_name"),
                    "shared_person_email": temp.get("shared_person_email"),
                    "shared_person_phone": temp.get("shared_person_phone"),
                    "who_paid": temp.get("who_paid", "You"),
                    "is_recurring": False,
                    "recurring_interval": "None"
                }
                
                # Check for duplication to prevent repeat triggers
                dup_check = supabase.table("expenses").select("id").eq("profile_id", user_id).eq("date", new_expense["date"]).eq("merchant", new_expense["merchant"]).eq("amount", new_expense["amount"]).execute()
                if not dup_check.data:
                    supabase.table("expenses").insert(new_expense).execute()
                    
                current_due = next_due
                generated_any = True
                
            if generated_any:
                # Update the template's last_recurring_run date to avoid re-triggering
                supabase.table("expenses").update({"last_recurring_run": current_due.strftime("%Y-%m-%d")}).eq("id", temp["id"]).execute()
                
    except Exception as e:
        logger.error(f"Error processing recurring schedules: {e}")


# ==========================================================
# Next-Gen PFM Enhancements Helper Functions (June 21, 2026)
# ==========================================================

# --- Households Helpers ---
def get_household(profile_id: str) -> dict:
    """Checks if the user belongs to any household. Returns household details if found."""
    if not supabase:
        return {}
    try:
        # First check membership
        res = supabase.table("household_members").select("household_id, role, permissions").eq("profile_id", profile_id).execute()
        if res.data:
            membership = res.data[0]
            h_res = supabase.table("households").select("*").eq("id", membership["household_id"]).execute()
            if h_res.data:
                h_data = h_res.data[0]
                h_data["role"] = membership["role"]
                h_data["permissions"] = membership["permissions"]
                return h_data
    except Exception as e:
        logger.error(f"Error fetching household: {e}")
        raise e
    return {}

def get_household_members(household_id: str) -> list:
    """Fetches all members belonging to a household, including their profile details."""
    if not supabase:
        return []
    try:
        res = supabase.table("household_members").select("*, profiles(full_name, email, avatar_url)").eq("household_id", household_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching household members: {e}")
        raise e

def create_household(profile_id: str, name: str) -> dict:
    """Creates a new household and registers the profile as Admin."""
    if not supabase:
        return {}
    try:
        h_res = supabase.table("households").insert({"name": name}).execute()
        if h_res.data:
            h_id = h_res.data[0]["id"]
            m_res = supabase.table("household_members").insert({
                "household_id": h_id,
                "profile_id": profile_id,
                "role": "Admin",
                "permissions": {"can_view_shared_ledger": True, "can_view_child_balances": True, "private_individual_budget": False}
            }).execute()
            if m_res.data:
                return h_res.data[0]
    except Exception as e:
        logger.error(f"Error creating household: {e}")
        raise e
    return {}

def add_household_member(household_id: str, member_email: str, role: str = "Parent") -> bool:
    """Looks up a profile by email and links them to the household."""
    if not supabase:
        return False
    try:
        p_res = supabase.table("profiles").select("id").eq("email", member_email).execute()
        if p_res.data:
            p_id = p_res.data[0]["id"]
            m_res = supabase.table("household_members").insert({
                "household_id": household_id,
                "profile_id": p_id,
                "role": role,
                "permissions": {"can_view_shared_ledger": True, "can_view_child_balances": True, "private_individual_budget": True}
            }).execute()
            return len(m_res.data or []) > 0
    except Exception as e:
        logger.error(f"Error adding household member: {e}")
        raise e
    return False

# --- Goals Helpers ---
def get_goals(profile_id: str, household_id: str = None) -> list:
    """Fetches all personal goals and any shared goals in the household."""
    if not supabase:
        return []
    try:
        if household_id:
            res = supabase.table("goals").select("*").or_(f"profile_id.eq.{profile_id},household_id.eq.{household_id}").execute()
        else:
            res = supabase.table("goals").select("*").eq("profile_id", profile_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching goals: {e}")
        raise e

def insert_goal(goal_data: dict) -> dict:
    """Creates a new financial goal."""
    if not supabase:
        return {}
    try:
        res = supabase.table("goals").insert(goal_data).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Error inserting goal: {e}")
        raise e
    return {}

def update_goal_savings(goal_id: str, savings_amount: float) -> bool:
    """Updates the saved amount for a goal."""
    if not supabase:
        return False
    try:
        res = supabase.table("goals").update({"current_savings": savings_amount}).eq("id", goal_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error updating goal: {e}")
        raise e
    return False

def delete_goal(goal_id: str) -> bool:
    """Deletes a goal."""
    if not supabase:
        return False
    try:
        res = supabase.table("goals").delete().eq("id", goal_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error deleting goal: {e}")
        raise e
    return False

# --- Subscriptions Helpers ---
def get_subscriptions(profile_id: str) -> list:
    """Fetches active recurring subscriptions for a profile."""
    if not supabase:
        return []
    try:
        res = supabase.table("subscriptions").select("*, categories(name, svg_icon)").eq("profile_id", profile_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}")
        raise e

def insert_subscription(sub_data: dict) -> dict:
    """Registers a new recurring subscription."""
    if not supabase:
        return {}
    try:
        res = supabase.table("subscriptions").insert(sub_data).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Error inserting subscription: {e}")
        raise e
    return {}

def update_subscription(sub_id: str, updates: dict) -> bool:
    """Updates active subscription details (like wasted flag or last_detected_usage)."""
    if not supabase:
        return False
    try:
        res = supabase.table("subscriptions").update(updates).eq("id", sub_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        raise e
    return False

def delete_subscription(sub_id: str) -> bool:
    """Removes a subscription tracking record."""
    if not supabase:
        return False
    try:
        res = supabase.table("subscriptions").delete().eq("id", sub_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error deleting subscription: {e}")
        raise e
    return False

# --- Allowance & Chore Helpers ---
def get_allowances_for_parent(parent_id: str) -> list:
    """Gets allowances and linked child profiles managed by a parent."""
    if not supabase:
        return []
    try:
        res = supabase.table("allowances").select("*, profiles!child_id(full_name, email)").eq("parent_id", parent_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching parent allowances: {e}")
        raise e

def get_allowance_for_child(child_id: str) -> dict:
    """Gets allowance managed for a child profile."""
    if not supabase:
        return {}
    try:
        res = supabase.table("allowances").select("*, profiles!parent_id(full_name, email)").eq("child_id", child_id).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Error fetching child allowance: {e}")
        raise e
    return {}

def create_allowance(parent_id: str, child_email: str, base_pocket_money: float, guardrails: dict) -> dict:
    """Creates a parent-child allowance linking system."""
    if not supabase:
        return {}
    try:
        p_res = supabase.table("profiles").select("id").eq("email", child_email).execute()
        if p_res.data:
            c_id = p_res.data[0]["id"]
            res = supabase.table("allowances").insert({
                "parent_id": parent_id,
                "child_id": c_id,
                "base_pocket_money": base_pocket_money,
                "spending_guardrails": guardrails
            }).execute()
            if res.data:
                return res.data[0]
    except Exception as e:
        logger.error(f"Error creating allowance: {e}")
        raise e
    return {}

def get_chores(allowance_id: str) -> list:
    """Gets chores assigned within an allowance contract."""
    if not supabase:
        return []
    try:
        res = supabase.table("chores").select("*").eq("allowance_id", allowance_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching chores: {e}")
        raise e

def create_chore(allowance_id: str, assigned_to: str, name: str, reward: float, due_date: str) -> dict:
    """Creates a chore reward task."""
    if not supabase:
        return {}
    try:
        res = supabase.table("chores").insert({
            "allowance_id": allowance_id,
            "assigned_to": assigned_to,
            "name": name,
            "reward_amount": reward,
            "status": "Assigned",
            "due_date": due_date
        }).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Error creating chore: {e}")
        raise e
    return {}

def update_chore_status(chore_id: str, status: str) -> bool:
    """Updates chore completion state."""
    if not supabase:
        return False
    try:
        res = supabase.table("chores").update({"status": status}).eq("id", chore_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error updating chore: {e}")
        raise e
    return False

# --- What-If Scenarios Helpers ---
def get_scenarios(profile_id: str) -> list:
    """Fetches sandbox what-if cloned profiles."""
    if not supabase:
        return []
    try:
        res = supabase.table("what_if_scenarios").select("*").eq("profile_id", profile_id).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Error fetching scenarios: {e}")
        raise e

def save_scenario(profile_id: str, name: str, inputs: dict, outputs: dict) -> dict:
    """Saves a sandbox timeline clone."""
    if not supabase:
        return {}
    try:
        res = supabase.table("what_if_scenarios").insert({
            "profile_id": profile_id,
            "scenario_name": name,
            "inputs": inputs,
            "outputs": outputs
        }).execute()
        if res.data:
            return res.data[0]
    except Exception as e:
        logger.error(f"Error saving scenario: {e}")
        raise e
    return {}

def delete_scenario(scenario_id: str) -> bool:
    """Deletes a sandbox scenario."""
    if not supabase:
        return False
    try:
        res = supabase.table("what_if_scenarios").delete().eq("id", scenario_id).execute()
        return len(res.data or []) > 0
    except Exception as e:
        logger.error(f"Error deleting scenario: {e}")
        raise e
    return False


