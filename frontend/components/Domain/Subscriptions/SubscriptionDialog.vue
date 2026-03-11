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
    <v-card-text class="px-3 px-sm-4 pt-3">
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
              density="comfortable"
              autocomplete="off"
              required
            />
          </v-col>

          <!-- Category + Color -->
          <v-col cols="8">
            <v-select
              v-model="form.category"
              label="Category"
              :items="categoryOptions"
              item-title="label"
              item-value="value"
              :prepend-inner-icon="categoryIcon(form.category)"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="4">
            <v-menu
              v-model="colorMenuOpen"
              :close-on-content-click="false"
              location="bottom"
            >
              <template #activator="{ props }">
                <v-btn
                  v-bind="props"
                  block
                  variant="outlined"
                  class="color-picker-btn"
                  style="height: 48px; border-color: rgba(128,128,128,0.4);"
                >
                  <span
                    class="color-swatch-preview mr-2"
                    :style="{ background: form.color }"
                  />
                  Color
                </v-btn>
              </template>
              <v-card class="pa-3" elevation="8">
                <div
                  class="color-grid"
                >
                  <button
                    v-for="c in colorPalette"
                    :key="c"
                    class="color-dot"
                    :class="{ 'color-dot--active': form.color === c }"
                    :style="{ background: c }"
                    type="button"
                    :aria-label="c"
                    @click="selectColor(c)"
                  >
                    <v-icon
                      v-if="form.color === c"
                      color="white"
                      size="16"
                    >
                      {{ $globals.icons.check }}
                    </v-icon>
                  </button>
                </div>
              </v-card>
            </v-menu>
          </v-col>

          <!-- Cost + Currency side by side -->
          <v-col cols="7">
            <v-text-field
              v-model.number="form.cost"
              label="Cost"
              type="number"
              min="0"
              step="0.01"
              inputmode="decimal"
              :prepend-inner-icon="$globals.icons.chart"
              :rules="[v => (v !== null && v !== '' && v >= 0) || 'Enter a valid cost']"
              variant="outlined"
              density="comfortable"
            />
          </v-col>
          <v-col cols="5">
            <v-select
              v-model="form.currency"
              label="Currency"
              :items="currencies"
              variant="outlined"
              density="comfortable"
            />
          </v-col>

          <!-- Billing Cycle -->
          <v-col cols="12">
            <v-select
              v-model="form.billingCycle"
              label="Billing Cycle"
              :items="billingCycleOptions"
              item-title="label"
              item-value="value"
              :prepend-inner-icon="$globals.icons.calendarWeek"
              variant="outlined"
              density="comfortable"
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
              density="comfortable"
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
              density="comfortable"
            />
          </v-col>

          <!-- Active toggle -->
          <v-col cols="12">
            <v-switch
              v-model="form.active"
              color="primary"
              hide-details
              label="Active subscription"
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
const colorMenuOpen = ref(false);

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
  "#5C6BC0",
  "#42A5F5",
  "#26C6DA",
  "#26A69A",
  "#66BB6A",
  "#D4E157",
  "#FFCA28",
  "#FFA726",
  "#EF5350",
  "#EC407A",
  "#AB47BC",
  "#78909C",
];

function selectColor(c: string) {
  form.value.color = c;
  colorMenuOpen.value = false;
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

.color-swatch-preview {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

/* 4-column grid of big, easy-to-tap colour dots */
.color-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.color-dot {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.1s ease, border-color 0.1s ease;
  -webkit-tap-highlight-color: transparent;
}

.color-dot:active {
  transform: scale(0.9);
}

.color-dot--active {
  border-color: rgba(0, 0, 0, 0.4);
  transform: scale(1.1);
}
</style>
