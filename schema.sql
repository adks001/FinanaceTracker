-- 1. Enable UUID Extension if not already present
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Drop existing triggers and functions if they exist to allow clean re-runs
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- 3. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_no TEXT UNIQUE,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Categories Table
CREATE TABLE IF NOT EXISTS public.categories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE, -- NULL for global/system categories
    name TEXT NOT NULL,
    svg_icon TEXT NOT NULL, -- Raw inline SVG paths
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Indexes for Category Uniqueness
-- Prevent duplicate names in global categories (profile_id is NULL)
DROP INDEX IF EXISTS idx_categories_global_name;
CREATE UNIQUE INDEX idx_categories_global_name ON public.categories (LOWER(name)) WHERE profile_id IS NULL;

-- Prevent duplicate names for custom user categories (profile_id is NOT NULL)
DROP INDEX IF EXISTS idx_categories_user_name;
CREATE UNIQUE INDEX idx_categories_user_name ON public.categories (profile_id, LOWER(name)) WHERE profile_id IS NOT NULL;

-- 6. Expenses Table
CREATE TABLE IF NOT EXISTS public.expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    merchant TEXT NOT NULL,
    description TEXT,
    amount NUMERIC(12, 2) NOT NULL CHECK (amount >= 0),
    earning_vs_expense TEXT NOT NULL CHECK (earning_vs_expense IN ('Earning', 'Expense')),
    category_id BIGINT REFERENCES public.categories(id) ON DELETE SET NULL,
    is_shared BOOLEAN DEFAULT FALSE NOT NULL,
    split_percentage NUMERIC(5, 2) DEFAULT 100.00 NOT NULL CHECK (split_percentage >= 0 AND split_percentage <= 100.00),
    shared_person_name TEXT,
    shared_person_email TEXT,
    shared_person_phone TEXT,
    who_paid TEXT CHECK (who_paid IN ('You', 'Other')) DEFAULT 'You',
    is_recurring BOOLEAN DEFAULT FALSE NOT NULL,
    recurring_interval TEXT CHECK (recurring_interval IN ('Weekly', 'Monthly', 'Yearly', 'None')) DEFAULT 'None',
    last_recurring_run DATE,
    raw_email_uid TEXT UNIQUE, -- Capture unique message key/hash to avoid parsing duplicates
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Automated Profile Creation Trigger
-- When a user registers in auth.users, create a profile row in public.profiles automatically.
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, phone_no, created_at)
    VALUES (
        NEW.id,
        COALESCE(
            NEW.raw_user_meta_data->>'full_name', 
            NEW.raw_user_meta_data->>'name', 
            split_part(NEW.email, '@', 1)
        ),
        NEW.email,
        NEW.raw_user_meta_data->>'phone_no',
        COALESCE(NEW.created_at, now())
    );
    RETURN NEW;
EXCEPTION
    WHEN others THEN
        -- If something goes wrong (e.g. duplicate phone_no or email conflict), log it or allow manual signup fallback
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 8. Enable Row-Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;

-- 9. Row-Level Security (RLS) Policies

-- Profiles Policies
DROP POLICY IF EXISTS "Allow users to read their own profile" ON public.profiles;
CREATE POLICY "Allow users to read their own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Allow users to update their own profile" ON public.profiles;
CREATE POLICY "Allow users to update their own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id) WITH CHECK (auth.uid() = id);

DROP POLICY IF EXISTS "Allow users to insert their own profile" ON public.profiles;
CREATE POLICY "Allow users to insert their own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Categories Policies
DROP POLICY IF EXISTS "Allow users to read global and their own categories" ON public.categories;
CREATE POLICY "Allow users to read global and their own categories" ON public.categories
    FOR SELECT USING (profile_id IS NULL OR auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to insert their own categories" ON public.categories;
CREATE POLICY "Allow users to insert their own categories" ON public.categories
    FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to update their own categories" ON public.categories;
CREATE POLICY "Allow users to update their own categories" ON public.categories
    FOR UPDATE USING (auth.uid() = profile_id) WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to delete their own categories" ON public.categories;
CREATE POLICY "Allow users to delete their own categories" ON public.categories
    FOR DELETE USING (auth.uid() = profile_id);

-- Expenses Policies
DROP POLICY IF EXISTS "Allow users to read their own expenses" ON public.expenses;
CREATE POLICY "Allow users to read their own expenses" ON public.expenses
    FOR SELECT USING (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to insert their own expenses" ON public.expenses;
CREATE POLICY "Allow users to insert their own expenses" ON public.expenses
    FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to update their own expenses" ON public.expenses;
CREATE POLICY "Allow users to update their own expenses" ON public.expenses
    FOR UPDATE USING (auth.uid() = profile_id) WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to delete their own expenses" ON public.expenses;
CREATE POLICY "Allow users to delete their own expenses" ON public.expenses
    FOR DELETE USING (auth.uid() = profile_id);

-- 10. Seed Global Categories
INSERT INTO public.categories (profile_id, name, svg_icon)
VALUES
  -- Earnings
  (NULL, 'Salary Credit', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'),
  (NULL, 'Investments & Trading', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>'),
  (NULL, 'Retirement & PF', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'),
  (NULL, 'Profits & Interest', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 22v-2h18v2H3zm2-3v-7h3v7H5zm5 0v-9h3v7h-3zm5 0V7h3v12h-3zm5 0V4h3v15h-3z"></path></svg>'),
  (NULL, 'F&F Settlement (Receipts)', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'),
  (NULL, 'Other Income', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'),
  -- Expenses
  (NULL, 'Loans & EMI', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"></line><circle cx="6.5" cy="6.5" r="2.5"></circle><circle cx="17.5" cy="17.5" r="2.5"></circle></svg>'),
  (NULL, 'Credit Card Payments', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>'),
  (NULL, 'Settlements & Splits', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'),
  (NULL, 'School & Tuition Fees', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"></path><path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path></svg>'),
  (NULL, 'Groceries', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>'),
  (NULL, 'Fuel & Transport', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><circle cx="17" cy="17" r="2"></circle><path d="M13 17H9"></path></svg>'),
  (NULL, 'Dining & Food', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>'),
  (NULL, 'Utilities & Bills', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>'),
  (NULL, 'Medical & Health', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'),
  (NULL, 'Entertainment & Subs', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>'),
  (NULL, 'Home Maintenance', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path></svg>'),
  (NULL, 'Miscellaneous', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>')
ON CONFLICT (LOWER(name)) WHERE profile_id IS NULL 
DO NOTHING;

-- Migration script to alter existing tables
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS avatar_url TEXT;
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS shared_person_name TEXT;
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS shared_person_email TEXT;
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS shared_person_phone TEXT;
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS who_paid TEXT CHECK (who_paid IN ('You', 'Other')) DEFAULT 'You';
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE NOT NULL;
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS recurring_interval TEXT CHECK (recurring_interval IN ('Weekly', 'Monthly', 'Yearly', 'None')) DEFAULT 'None';
ALTER TABLE public.expenses ADD COLUMN IF NOT EXISTS last_recurring_run DATE;


-- ==========================================================
-- Next-Gen PFM Enhancements Schema Extension (June 21, 2026)
-- ==========================================================

-- 11. Households Table (Logical containment of Families)
CREATE TABLE IF NOT EXISTS public.households (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 12. Household Members Table (RLS and Permissions Mapping)
CREATE TABLE IF NOT EXISTS public.household_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES public.households(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Parent', 'Child', 'Admin')),
    permissions JSONB NOT NULL DEFAULT '{"can_view_shared_ledger": true, "can_view_child_balances": true, "private_individual_budget": true}',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(household_id, profile_id)
);

-- 13. Dynamic Financial Goals Table
CREATE TABLE IF NOT EXISTS public.goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES public.households(id) ON DELETE CASCADE,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    target_amount NUMERIC(15, 2) NOT NULL CHECK (target_amount > 0),
    current_savings NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    target_date DATE NOT NULL,
    linked_assets JSONB NOT NULL DEFAULT '[]', -- References bank accounts or investment portfolio IDs
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 14. Intelligent Subscriptions & Recurring Transactions Table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    billing_cycle VARCHAR(50) NOT NULL CHECK (billing_cycle IN ('Weekly', 'Monthly', 'Quarterly', 'Yearly')),
    next_billing_date DATE NOT NULL,
    category_id BIGINT REFERENCES public.categories(id) ON DELETE SET NULL,
    last_detected_usage TIMESTAMPTZ,
    is_wasted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 15. Parent-Child Chore and Allowance Tables
CREATE TABLE IF NOT EXISTS public.allowances (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    child_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    base_pocket_money NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    payout_interval VARCHAR(50) DEFAULT 'Monthly',
    spending_guardrails JSONB NOT NULL DEFAULT '{"daily_limit": 500, "blocked_categories": ["Gaming", "Entertainment"], "approvals_required_above": 1000}',
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.chores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    allowance_id UUID REFERENCES public.allowances(id) ON DELETE CASCADE,
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    reward_amount NUMERIC(15, 2) NOT NULL CHECK (reward_amount >= 0),
    status VARCHAR(50) NOT NULL CHECK (status IN ('Assigned', 'Completed', 'Approved')),
    due_date DATE,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 16. What-If Sandbox Scenarios Table
CREATE TABLE IF NOT EXISTS public.what_if_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    scenario_name VARCHAR(255) NOT NULL,
    inputs JSONB NOT NULL, -- Inputs like '{"income_delta": 20000, "rent_delta": -5000, "has_new_child": true}'
    outputs JSONB NOT NULL, -- Computed targets and runway simulations
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 17. Enable Row-Level Security (RLS)
ALTER TABLE public.households ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.household_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.goals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.allowances ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.what_if_scenarios ENABLE ROW LEVEL SECURITY;

-- 18. Row-Level Security (RLS) Security Definer Functions (To prevent infinite recursion)
CREATE OR REPLACE FUNCTION public.check_user_in_household(h_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.household_members
    WHERE household_members.household_id = h_id AND household_members.profile_id = auth.uid()
  );
$$ LANGUAGE sql SECURITY DEFINER SET search_path = '';

CREATE OR REPLACE FUNCTION public.check_user_is_admin_or_parent(h_id UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.household_members
    WHERE household_members.household_id = h_id AND household_members.profile_id = auth.uid() AND household_members.role IN ('Parent', 'Admin')
  );
$$ LANGUAGE sql SECURITY DEFINER SET search_path = '';

-- 19. Row-Level Security (RLS) Policies

-- Households Policy
DROP POLICY IF EXISTS "Allow members to read households" ON public.households;
CREATE POLICY "Allow members to read households" ON public.households
    FOR SELECT USING (
        public.check_user_in_household(id)
    );

DROP POLICY IF EXISTS "Allow authenticated users to insert households" ON public.households;
CREATE POLICY "Allow authenticated users to insert households" ON public.households
    FOR INSERT WITH CHECK (
        auth.uid() IS NOT NULL
    );

DROP POLICY IF EXISTS "Allow admins and parents to update households" ON public.households;
CREATE POLICY "Allow admins and parents to update households" ON public.households
    FOR UPDATE USING (
        public.check_user_is_admin_or_parent(id)
    ) WITH CHECK (
        public.check_user_is_admin_or_parent(id)
    );

DROP POLICY IF EXISTS "Allow admins and parents to delete households" ON public.households;
CREATE POLICY "Allow admins and parents to delete households" ON public.households
    FOR DELETE USING (
        public.check_user_is_admin_or_parent(id)
    );

-- Household Members Policy
DROP POLICY IF EXISTS "Allow members to view household_members" ON public.household_members;
CREATE POLICY "Allow members to view household_members" ON public.household_members
    FOR SELECT USING (
        profile_id = auth.uid() OR 
        public.check_user_in_household(household_id)
    );

DROP POLICY IF EXISTS "Allow members to insert household_members" ON public.household_members;
CREATE POLICY "Allow members to insert household_members" ON public.household_members
    FOR INSERT WITH CHECK (
        auth.uid() = profile_id OR 
        public.check_user_is_admin_or_parent(household_id)
    );

DROP POLICY IF EXISTS "Allow members to update household_members" ON public.household_members;
CREATE POLICY "Allow members to update household_members" ON public.household_members
    FOR UPDATE USING (
        profile_id = auth.uid() OR 
        public.check_user_is_admin_or_parent(household_id)
    ) WITH CHECK (
        profile_id = auth.uid() OR 
        public.check_user_is_admin_or_parent(household_id)
    );

DROP POLICY IF EXISTS "Allow members to delete household_members" ON public.household_members;
CREATE POLICY "Allow members to delete household_members" ON public.household_members
    FOR DELETE USING (
        profile_id = auth.uid() OR 
        public.check_user_is_admin_or_parent(household_id)
    );

-- Goals Policy (Read if owner or in same household)
DROP POLICY IF EXISTS "Allow users to read goals" ON public.goals;
CREATE POLICY "Allow users to read goals" ON public.goals
    FOR SELECT USING (
        auth.uid() = profile_id OR 
        (household_id IS NOT NULL AND public.check_user_in_household(household_id))
    );

DROP POLICY IF EXISTS "Allow users to insert goals" ON public.goals;
CREATE POLICY "Allow users to insert goals" ON public.goals
    FOR INSERT WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to update goals" ON public.goals;
CREATE POLICY "Allow users to update goals" ON public.goals
    FOR UPDATE USING (auth.uid() = profile_id) WITH CHECK (auth.uid() = profile_id);

DROP POLICY IF EXISTS "Allow users to delete goals" ON public.goals;
CREATE POLICY "Allow users to delete goals" ON public.goals
    FOR DELETE USING (auth.uid() = profile_id);

-- Subscriptions Policy
DROP POLICY IF EXISTS "Allow users to manage their own subscriptions" ON public.subscriptions;
CREATE POLICY "Allow users to manage their own subscriptions" ON public.subscriptions
    FOR ALL USING (auth.uid() = profile_id) WITH CHECK (auth.uid() = profile_id);

-- Allowances Policy (Read if parent or child)
DROP POLICY IF EXISTS "Allow parents and children to read allowances" ON public.allowances;
CREATE POLICY "Allow parents and children to read allowances" ON public.allowances
    FOR SELECT USING (auth.uid() = parent_id OR auth.uid() = child_id);

DROP POLICY IF EXISTS "Allow parents to manage allowances" ON public.allowances;
CREATE POLICY "Allow parents to manage allowances" ON public.allowances
    FOR ALL USING (auth.uid() = parent_id) WITH CHECK (auth.uid() = parent_id);

-- Chores Policy (Read if parent or assigned child)
DROP POLICY IF EXISTS "Allow parents and children to read chores" ON public.chores;
CREATE POLICY "Allow parents and children to read chores" ON public.chores
    FOR SELECT USING (
        auth.uid() = assigned_to OR 
        EXISTS (
            SELECT 1 FROM public.allowances a 
            WHERE a.id = allowance_id AND a.parent_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Allow parents and assigned children to update chores" ON public.chores;
CREATE POLICY "Allow parents and assigned children to update chores" ON public.chores
    FOR UPDATE USING (
        auth.uid() = assigned_to OR 
        EXISTS (
            SELECT 1 FROM public.allowances a 
            WHERE a.id = allowance_id AND a.parent_id = auth.uid()
        )
    );

DROP POLICY IF EXISTS "Allow parents to insert/delete chores" ON public.chores;
CREATE POLICY "Allow parents to insert/delete chores" ON public.chores
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.allowances a 
            WHERE a.id = allowance_id AND a.parent_id = auth.uid()
        )
    );

-- What-If Scenarios Policy
DROP POLICY IF EXISTS "Allow users to manage scenarios" ON public.what_if_scenarios;
CREATE POLICY "Allow users to manage scenarios" ON public.what_if_scenarios
    FOR ALL USING (auth.uid() = profile_id) WITH CHECK (auth.uid() = profile_id);


