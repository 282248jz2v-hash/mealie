<template>
  <BaseDialog
    v-model="dialog"
    :title="isEdit ? 'Edit Subscription' : 'Add Subscription'"
    :icon="$globals.icons.bellPlus"
    width="600"
    can-submit
    :submit-text="isEdit ? 'Save Changes' : 'Add Subscription'"
    @submit="onSubmit"
    @cancel="onCancel"
  >
    <v-card-text>
      <v-form
        ref="formRef"
        @submit.prevent
      >
        <v-row dense>
          <!-- Name -->
          <v-col cols="12">
            <v-text-field
              v-model="form.name"
              label="Service Name"
              placeholder="e.g. ChatGPT Plus, Netflix, Xbox Game Pass"
              :prepend-inner-icon="$globals.icons.bellAlert"
              :rules="[v => !!v || 'Name is required']"
              variant="outlined"
              density="compact"
              required
            />
          </v-col>

          <!-- Category + Color -->
          <v-col
            cols="8"
            sm="9"
          >
            <v-select
              v-model="form.category"
              label="Category"
              :items="categoryOptions"
              item-title="label"
              item-value="value"
              :prepend-inner-icon="categoryIcon(form.category)"
              variant="outlined"
              density="compact"
            />
          </v-col>
          <v-col
            cols="4"
            sm="3"
          >
            <v-menu :close-on-content-click="false">
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  block
                  variant="outlined"
                  style="height: 40px; border-color: rgba(0,0,0,0.38);"
                  class="color-picker-btn"
                >
                  <v-icon
                    start
                    :color="form.color"
                  >
                    {{ $globals.icons.formatColorFill }}
                  </v-icon>
                  Color
                </v-btn>
              </template>
              <v-card class="pa-3">
                <div class="d-flex flex-wrap ga-2" style="max-width: 200px">
                  <v-btn
                    v-for="c in colorPalette"
                    :key="c"
                    :color="c"
                    icon
                    size="small"
                    :variant="form.color === c ? 'elevated' : 'flat'"
                    @click="form.color = c"
                  >
                    <v-icon
                      v-if="form.color === c"
                      size="14"
                    >
                      {{ $globals.icons.check }}
                    </v-icon>
                  </v-btn>
                </div>
              </v-card>
            </v-menu>
          </v-col>

          <!-- Cost -->
          <v-col
            cols="6"
            sm="5"
          >
            <v-text-field
              v-model.number="form.cost"
              label="Cost"
              type="number"
              min="0"
              step="0.01"
              :prepend-inner-icon="$globals.icons.chart"
              :rules="[v => (v !== null && v !== '' && v >= 0) || 'Enter a valid cost']"
              variant="outlined"
              density="compact"
            />
          </v-col>

          <!-- Currency -->
          <v-col
            cols="6"
            sm="3"
          >
            <v-select
              v-model="form.currency"
              label="Currency"
              :items="currencies"
              variant="outlined"
              density="compact"
            />
          </v-col>

          <!-- Billing Cycle -->
          <v-col
            cols="12"
            sm="4"
          >
            <v-select
              v-model="form.billingCycle"
              label="Billing Cycle"
              :items="billingCycleOptions"
              item-title="label"
              item-value="value"
              :prepend-inner-icon="$globals.icons.calendarWeek"
              variant="outlined"
              density="compact"
            />
          </v-col>

          <!-- Next Renewal Date -->
          <v-col cols="12">
            <v-text-field
              v-model="form.nextRenewalDate"
              label="Next Renewal Date"
              type="date"
              :prepend-inner-icon="$globals.icons.calendarToday"
              :rules="[v => !!v || 'Renewal date is required']"
              variant="outlined"
              density="compact"
              required
            />
          </v-col>

          <!-- Notes -->
          <v-col cols="12">
            <v-textarea
              v-model="form.notes"
              label="Notes (optional)"
              rows="2"
              auto-grow
              variant="outlined"
              density="compact"
            />
          </v-col>

          <!-- Active toggle -->
          <v-col cols="12">
            <v-switch
              v-model="form.active"
              color="primary"
              hide-details
              label="Active subscription"
              density="compact"
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import type { SubscriptionForm, SubscriptionCategory, BillingCycle } from "~/composables/use-subscriptions";

interface Props {
  modelValue: boolean;
  editForm?: SubscriptionForm | null;
}

interface Emits {
  (e: "update:modelValue", val: boolean): void;
  (e: "submit", form: SubscriptionForm): void;
}

const props = withDefaults(defineProps<Props>(), {
  editForm: null,
});
const emit = defineEmits<Emits>();
const { $globals } = useNuxtApp();

const dialog = computed({
  get: () => props.modelValue,
  set: val => emit("update:modelValue", val),
});

const isEdit = computed(() => !!props.editForm);

const defaultForm = (): SubscriptionForm => ({
  name: "",
  category: "other",
  cost: null,
  currency: "USD",
  billingCycle: "monthly",
  nextRenewalDate: "",
  color: "#5C6BC0",
  notes: "",
  active: true,
});

const form = ref<SubscriptionForm>(defaultForm());

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      form.value = props.editForm ? { ...props.editForm } : defaultForm();
    }
  },
);

const categoryOptions: { label: string; value: SubscriptionCategory }[] = [
  { label: "AI Tools", value: "ai" },
  { label: "Gaming", value: "gaming" },
  { label: "Streaming", value: "streaming" },
  { label: "Software", value: "software" },
  { label: "Other", value: "other" },
];

const billingCycleOptions: { label: string; value: BillingCycle }[] = [
  { label: "Weekly", value: "weekly" },
  { label: "Monthly", value: "monthly" },
  { label: "Yearly", value: "yearly" },
];

const currencies = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY"];

const colorPalette = [
  "#5C6BC0", // indigo
  "#42A5F5", // blue
  "#26C6DA", // cyan
  "#26A69A", // teal
  "#66BB6A", // green
  "#D4E157", // lime
  "#FFCA28", // amber
  "#FFA726", // orange
  "#EF5350", // red
  "#EC407A", // pink
  "#AB47BC", // purple
  "#78909C", // blue-grey
];

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

function onSubmit() {
  if (!form.value.name || form.value.cost === null || !form.value.nextRenewalDate) return;
  emit("submit", { ...form.value });
  dialog.value = false;
}

function onCancel() {
  dialog.value = false;
}
</script>

<style scoped>
.color-picker-btn {
  text-transform: none;
  letter-spacing: 0;
}
</style>
