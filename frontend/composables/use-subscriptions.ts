export type BillingCycle = "weekly" | "monthly" | "yearly";
export type SubscriptionCategory = "ai" | "gaming" | "streaming" | "software" | "other";

export interface Subscription {
  id: string;
  name: string;
  category: SubscriptionCategory;
  cost: number;
  currency: string;
  billingCycle: BillingCycle;
  nextRenewalDate: string; // ISO date string YYYY-MM-DD
  color: string;
  notes: string;
  active: boolean;
  createdAt: string;
}

export interface SubscriptionForm {
  name: string;
  category: SubscriptionCategory;
  cost: number | null;
  currency: string;
  billingCycle: BillingCycle;
  nextRenewalDate: string;
  color: string;
  notes: string;
  active: boolean;
}

const STORAGE_KEY = "mealie_subscriptions";

function generateId(): string {
  return `sub_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

function loadFromStorage(): Subscription[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as Subscription[];
  }
  catch {
    return [];
  }
}

function saveToStorage(items: Subscription[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

// Shared reactive state across all composable instances
const subscriptions = ref<Subscription[]>([]);
let initialized = false;

export function useSubscriptions() {
  if (!initialized) {
    if (typeof window !== "undefined") {
      subscriptions.value = loadFromStorage();
      initialized = true;
    }
  }

  function add(form: SubscriptionForm): Subscription {
    const newSub: Subscription = {
      id: generateId(),
      name: form.name,
      category: form.category,
      cost: form.cost ?? 0,
      currency: form.currency,
      billingCycle: form.billingCycle,
      nextRenewalDate: form.nextRenewalDate,
      color: form.color,
      notes: form.notes,
      active: form.active,
      createdAt: new Date().toISOString(),
    };
    subscriptions.value = [...subscriptions.value, newSub];
    saveToStorage(subscriptions.value);
    return newSub;
  }

  function update(id: string, form: SubscriptionForm) {
    subscriptions.value = subscriptions.value.map(sub =>
      sub.id === id
        ? {
            ...sub,
            name: form.name,
            category: form.category,
            cost: form.cost ?? 0,
            currency: form.currency,
            billingCycle: form.billingCycle,
            nextRenewalDate: form.nextRenewalDate,
            color: form.color,
            notes: form.notes,
            active: form.active,
          }
        : sub,
    );
    saveToStorage(subscriptions.value);
  }

  function remove(id: string) {
    subscriptions.value = subscriptions.value.filter(sub => sub.id !== id);
    saveToStorage(subscriptions.value);
  }

  /** Cost normalised to a monthly amount */
  function toMonthlyCost(sub: Subscription): number {
    if (!sub.active) return 0;
    if (sub.billingCycle === "monthly") return sub.cost;
    if (sub.billingCycle === "yearly") return sub.cost / 12;
    if (sub.billingCycle === "weekly") return sub.cost * 4.33;
    return sub.cost;
  }

  /** Cost normalised to a yearly amount */
  function toYearlyCost(sub: Subscription): number {
    if (!sub.active) return 0;
    if (sub.billingCycle === "monthly") return sub.cost * 12;
    if (sub.billingCycle === "yearly") return sub.cost;
    if (sub.billingCycle === "weekly") return sub.cost * 52;
    return sub.cost;
  }

  function daysUntilRenewal(sub: Subscription): number {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const renewal = new Date(sub.nextRenewalDate);
    renewal.setHours(0, 0, 0, 0);
    return Math.round((renewal.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  }

  const totalMonthlyCost = computed(() =>
    subscriptions.value.reduce((sum, sub) => sum + toMonthlyCost(sub), 0),
  );

  const totalYearlyCost = computed(() =>
    subscriptions.value.reduce((sum, sub) => sum + toYearlyCost(sub), 0),
  );

  const upcomingRenewals = computed(() =>
    subscriptions.value
      .filter(sub => sub.active && daysUntilRenewal(sub) >= 0 && daysUntilRenewal(sub) <= 7)
      .sort((a, b) => daysUntilRenewal(a) - daysUntilRenewal(b)),
  );

  return {
    subscriptions,
    add,
    update,
    remove,
    toMonthlyCost,
    toYearlyCost,
    daysUntilRenewal,
    totalMonthlyCost,
    totalYearlyCost,
    upcomingRenewals,
  };
}
