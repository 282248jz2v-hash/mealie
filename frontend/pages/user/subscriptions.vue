<template>
  <v-container
    class="pb-20 px-2 px-sm-4"
    style="max-width: 1200px"
  >
    <!-- Add / Edit dialog -->
    <SubscriptionDialog
      v-model="dialogOpen"
      :edit-form="editTarget"
      @submit="onDialogSubmit"
    />

    <!-- Delete confirmation -->
    <BaseDialog
      v-model="deleteDialog"
      title="Delete Subscription"
      color="error"
      :icon="$globals.icons.delete"
      can-confirm
      @confirm="onConfirmDelete"
    >
      <v-card-text>
        Are you sure you want to delete <strong>{{ deleteTarget?.name }}</strong>? This cannot be undone.
      </v-card-text>
    </BaseDialog>

    <!-- ─── Page header ─────────────────────────────────── -->
    <div class="d-flex align-center mt-3 mb-5">
      <div class="flex-grow-1 min-width-0">
        <h1 class="font-weight-bold d-flex align-center ga-2 text-h5 text-sm-h4">
          <v-icon
            color="primary"
            size="28"
          >
            {{ $globals.icons.bellAlert }}
          </v-icon>
          Subscription Auditor
        </h1>
        <p class="text-caption text-sm-body-2 text-medium-emphasis mt-1 mb-0">
          Track recurring costs and get alerted before renewals.
        </p>
      </div>
      <!-- Only show text button on sm+ — on xs we use the FAB -->
      <v-btn
        color="primary"
        :prepend-icon="$globals.icons.createAlt"
        rounded="lg"
        class="d-none d-sm-flex ml-3 flex-shrink-0"
        @click="openAddDialog"
      >
        Add Subscription
      </v-btn>
    </div>

    <!-- ─── Upcoming renewal alerts ─────────────────────── -->
    <template v-if="upcomingRenewals.length">
      <v-alert
        v-for="sub in upcomingRenewals"
        :key="sub.id"
        type="warning"
        variant="tonal"
        border="start"
        class="mb-2"
        density="compact"
        :icon="$globals.icons.bellAlert"
        closable
      >
        <span class="font-weight-medium">{{ sub.name }}</span>
        renews <strong>{{ renewalLabel(sub) }}</strong>
        — {{ formatCurrency(sub.cost, sub.currency) }}/{{ sub.billingCycle }}
      </v-alert>
    </template>

    <!-- ─── Stats row ──────────────────────────────────── -->
    <v-row
      dense
      class="mb-3"
    >
      <v-col
        v-for="stat in statsCards"
        :key="stat.label"
        cols="6"
        sm="3"
      >
        <v-card
          variant="tonal"
          :color="stat.color"
          rounded="lg"
          class="pa-3 text-center"
        >
          <div class="text-caption text-uppercase font-weight-bold opacity-70 text-truncate">
            {{ stat.label }}
          </div>
          <div class="text-h6 text-sm-h5 font-weight-bold mt-1 text-truncate">
            {{ stat.value }}
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- ─── Filter / Sort bar ──────────────────────────── -->
    <!-- Category chips — horizontal scroll on mobile, no wrap -->
    <div class="mb-2 filter-scroll-row">
      <v-chip-group
        v-model="selectedCategory"
        selected-class="text-primary font-weight-bold"
        mandatory
      >
        <v-chip
          value="all"
          variant="outlined"
          size="small"
        >
          All
        </v-chip>
        <v-chip
          v-for="cat in categoryOptions"
          :key="cat.value"
          :value="cat.value"
          :prepend-icon="categoryIcon(cat.value)"
          variant="outlined"
          size="small"
        >
          {{ cat.label }}
        </v-chip>
      </v-chip-group>
    </div>

    <!-- Sort — icon-only on xs, labelled on sm+ -->
    <div class="d-flex align-center justify-end mb-4">
      <span class="text-caption text-medium-emphasis mr-2">Sort:</span>
      <v-btn-toggle
        v-model="sortKey"
        mandatory
        density="compact"
        variant="outlined"
        divided
        rounded="lg"
      >
        <v-btn
          value="renewal"
          size="small"
          :icon="$vuetify.display.xs ? $globals.icons.calendarToday : undefined"
          :prepend-icon="!$vuetify.display.xs ? $globals.icons.calendarToday : undefined"
        >
          <span class="d-none d-sm-inline">Renewal</span>
        </v-btn>
        <v-btn
          value="cost"
          size="small"
          :icon="$vuetify.display.xs ? $globals.icons.chart : undefined"
          :prepend-icon="!$vuetify.display.xs ? $globals.icons.chart : undefined"
        >
          <span class="d-none d-sm-inline">Cost</span>
        </v-btn>
        <v-btn
          value="name"
          size="small"
          :icon="$vuetify.display.xs ? $globals.icons.sortAlphabeticalAscending : undefined"
          :prepend-icon="!$vuetify.display.xs ? $globals.icons.sortAlphabeticalAscending : undefined"
        >
          <span class="d-none d-sm-inline">Name</span>
        </v-btn>
      </v-btn-toggle>
    </div>

    <!-- ─── Empty state ────────────────────────────────── -->
    <div
      v-if="!filteredSubscriptions.length"
      class="d-flex flex-column align-center justify-center py-12"
    >
      <v-icon
        size="64"
        color="grey-lighten-1"
      >
        {{ $globals.icons.bellPlus }}
      </v-icon>
      <p class="text-h6 text-medium-emphasis mt-4 text-center px-4">
        {{ subscriptions.length === 0 ? 'No subscriptions yet' : 'No subscriptions match this filter' }}
      </p>
      <v-btn
        v-if="subscriptions.length === 0"
        color="primary"
        variant="text"
        class="mt-2"
        :prepend-icon="$globals.icons.createAlt"
        @click="openAddDialog"
      >
        Add your first subscription
      </v-btn>
    </div>

    <!-- ─── Subscription list ──────────────────────────── -->
    <v-row
      v-else
      dense
    >
      <v-col
        v-for="sub in filteredSubscriptions"
        :key="sub.id"
        cols="12"
        sm="6"
        lg="4"
      >
        <v-card
          rounded="lg"
          class="subscription-card h-100"
          :style="{ borderLeft: `5px solid ${sub.color}` }"
          variant="outlined"
        >
          <!-- Card header -->
          <v-card-item class="py-2 px-3">
            <template #prepend>
              <v-avatar
                :color="sub.color"
                size="38"
              >
                <v-icon
                  size="20"
                  color="white"
                >
                  {{ categoryIcon(sub.category) }}
                </v-icon>
              </v-avatar>
            </template>
            <v-card-title class="text-subtitle-1 font-weight-bold pa-0">
              {{ sub.name }}
            </v-card-title>
            <v-card-subtitle class="pa-0">
              {{ categoryLabel(sub.category) }}
            </v-card-subtitle>
            <template #append>
              <v-chip
                :color="sub.active ? 'success' : 'grey'"
                size="x-small"
                variant="tonal"
              >
                {{ sub.active ? 'Active' : 'Paused' }}
              </v-chip>
            </template>
          </v-card-item>

          <v-card-text class="pt-1 pb-2 px-3">
            <!-- Cost row -->
            <div class="d-flex align-center flex-wrap ga-1 mb-1">
              <v-icon
                size="15"
                color="secondary"
              >
                {{ $globals.icons.chart }}
              </v-icon>
              <span class="text-subtitle-1 font-weight-bold">
                {{ formatCurrency(sub.cost, sub.currency) }}
              </span>
              <span class="text-caption text-medium-emphasis">/ {{ sub.billingCycle }}</span>
              <span
                v-if="sub.billingCycle !== 'monthly'"
                class="text-caption text-medium-emphasis"
              >
                ({{ formatCurrency(toMonthlyCost(sub), sub.currency) }}/mo)
              </span>
            </div>

            <!-- Renewal row -->
            <div
              class="d-flex align-center ga-1"
              :class="renewalUrgencyClass(sub)"
            >
              <v-icon size="15">
                {{ $globals.icons.calendarToday }}
              </v-icon>
              <span class="text-body-2">
                {{ renewalLabel(sub) }}
                <span class="text-caption opacity-70">({{ formatDate(sub.nextRenewalDate) }})</span>
              </span>
            </div>

            <!-- Notes -->
            <p
              v-if="sub.notes"
              class="text-caption text-medium-emphasis mt-2 mb-0"
              style="white-space: pre-line; line-height: 1.4;"
            >
              {{ sub.notes }}
            </p>
          </v-card-text>

          <v-divider class="mx-3" />

          <!-- Tall action row for easy tapping -->
          <v-card-actions class="px-2 py-0" style="min-height: 52px">
            <v-btn
              variant="text"
              :prepend-icon="$globals.icons.edit"
              style="min-height: 44px"
              @click="openEditDialog(sub)"
            >
              Edit
            </v-btn>
            <v-spacer />
            <v-btn
              variant="text"
              color="error"
              :prepend-icon="$globals.icons.delete"
              style="min-height: 44px"
              @click="openDeleteDialog(sub)"
            >
              Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- ─── FAB (mobile only) ──────────────────────────── -->
    <v-fab
      class="d-flex d-sm-none"
      color="primary"
      :icon="$globals.icons.createAlt"
      location="bottom end"
      size="large"
      app
      @click="openAddDialog"
    />
  </v-container>
</template>

<script lang="ts">
import { useSubscriptions } from "~/composables/use-subscriptions";
import type { Subscription, SubscriptionForm, SubscriptionCategory } from "~/composables/use-subscriptions";
import SubscriptionDialog from "~/components/Domain/Subscriptions/SubscriptionDialog.vue";

export default defineNuxtComponent({
  name: "UserSubscriptions",
  components: { SubscriptionDialog },

  setup() {
    const { $globals } = useNuxtApp();
    const {
      subscriptions,
      add,
      update,
      remove,
      toMonthlyCost,
      totalMonthlyCost,
      totalYearlyCost,
      upcomingRenewals,
      daysUntilRenewal,
    } = useSubscriptions();

    useSeoMeta({ title: "Subscription Auditor" });

    // ── Dialog state ──────────────────────────────────────
    const dialogOpen = ref(false);
    const editTarget = ref<SubscriptionForm | null>(null);
    const editTargetId = ref<string | null>(null);

    const deleteDialog = ref(false);
    const deleteTarget = ref<Subscription | null>(null);

    function openAddDialog() {
      editTarget.value = null;
      editTargetId.value = null;
      dialogOpen.value = true;
    }

    function openEditDialog(sub: Subscription) {
      editTargetId.value = sub.id;
      editTarget.value = {
        name: sub.name,
        category: sub.category,
        cost: sub.cost,
        currency: sub.currency,
        billingCycle: sub.billingCycle,
        nextRenewalDate: sub.nextRenewalDate,
        color: sub.color,
        notes: sub.notes,
        active: sub.active,
      };
      dialogOpen.value = true;
    }

    function onDialogSubmit(form: SubscriptionForm) {
      if (editTargetId.value) {
        update(editTargetId.value, form);
      }
      else {
        add(form);
      }
      editTargetId.value = null;
      editTarget.value = null;
    }

    function openDeleteDialog(sub: Subscription) {
      deleteTarget.value = sub;
      deleteDialog.value = true;
    }

    function onConfirmDelete() {
      if (deleteTarget.value) {
        remove(deleteTarget.value.id);
        deleteTarget.value = null;
      }
    }

    // ── Filtering / sorting ───────────────────────────────
    const selectedCategory = ref<string>("all");
    const sortKey = ref<"renewal" | "cost" | "name">("renewal");

    const categoryOptions: { label: string; value: SubscriptionCategory }[] = [
      { label: "AI Tools", value: "ai" },
      { label: "Gaming", value: "gaming" },
      { label: "Streaming", value: "streaming" },
      { label: "Software", value: "software" },
      { label: "Other", value: "other" },
    ];

    const filteredSubscriptions = computed(() => {
      let items = [...subscriptions.value];

      if (selectedCategory.value && selectedCategory.value !== "all") {
        items = items.filter(s => s.category === selectedCategory.value);
      }

      items.sort((a, b) => {
        if (sortKey.value === "renewal") {
          return new Date(a.nextRenewalDate).getTime() - new Date(b.nextRenewalDate).getTime();
        }
        if (sortKey.value === "cost") {
          return toMonthlyCost(b) - toMonthlyCost(a);
        }
        return a.name.localeCompare(b.name);
      });

      return items;
    });

    const activeCount = computed(() => subscriptions.value.filter(s => s.active).length);

    // ── Stats ─────────────────────────────────────────────
    const statsCards = computed(() => [
      {
        label: "Monthly",
        value: formatCurrency(totalMonthlyCost.value, "USD"),
        color: "primary",
      },
      {
        label: "Yearly",
        value: formatCurrency(totalYearlyCost.value, "USD"),
        color: "secondary",
      },
      {
        label: "Soon",
        value: String(upcomingRenewals.value.length),
        color: upcomingRenewals.value.length ? "warning" : "success",
      },
      {
        label: "Active",
        value: String(activeCount.value),
        color: "info",
      },
    ]);

    // ── Helpers ───────────────────────────────────────────
    function formatCurrency(amount: number, currency: string): string {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: currency || "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }).format(amount);
    }

    function formatDate(dateStr: string): string {
      const d = new Date(dateStr + "T00:00:00");
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    }

    function renewalLabel(sub: Subscription): string {
      const days = daysUntilRenewal(sub);
      if (days < 0) return `overdue ${Math.abs(days)}d`;
      if (days === 0) return "today";
      if (days === 1) return "tomorrow";
      return `in ${days}d`;
    }

    function renewalUrgencyClass(sub: Subscription): string {
      const days = daysUntilRenewal(sub);
      if (days < 0) return "text-error";
      if (days <= 3) return "text-error";
      if (days <= 7) return "text-warning";
      return "text-medium-emphasis";
    }

    const categoryLabelMap: Record<SubscriptionCategory, string> = {
      ai: "AI Tools",
      gaming: "Gaming",
      streaming: "Streaming",
      software: "Software",
      other: "Other",
    };

    function categoryLabel(cat: SubscriptionCategory): string {
      return categoryLabelMap[cat] ?? "Other";
    }

    function categoryIcon(cat: SubscriptionCategory): string {
      const map: Record<SubscriptionCategory, string> = {
        ai: $globals.icons.robot,
        gaming: $globals.icons.slotMachine,
        streaming: $globals.icons.viewDashboard,
        software: $globals.icons.desktopTowerMonitor,
        other: $globals.icons.tagArrowRight,
      };
      return map[cat] ?? $globals.icons.tagArrowRight;
    }

    return {
      subscriptions,
      filteredSubscriptions,
      upcomingRenewals,
      statsCards,
      toMonthlyCost,
      // dialog
      dialogOpen,
      editTarget,
      deleteDialog,
      deleteTarget,
      openAddDialog,
      openEditDialog,
      onDialogSubmit,
      openDeleteDialog,
      onConfirmDelete,
      // filter/sort
      selectedCategory,
      sortKey,
      categoryOptions,
      // helpers
      formatCurrency,
      formatDate,
      renewalLabel,
      renewalUrgencyClass,
      categoryLabel,
      categoryIcon,
    };
  },
});
</script>

<style scoped>
.subscription-card {
  transition: box-shadow 0.15s ease;
}
.subscription-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12) !important;
}

/* Horizontally scrollable filter row — no line wrap, hides scrollbar visually */
.filter-scroll-row {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}
.filter-scroll-row::-webkit-scrollbar {
  display: none;
}
</style>
