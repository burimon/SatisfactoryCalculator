import {
  BELT_CAPACITY_OPTIONS,
  MAX_ZOOM,
  MIN_ZOOM,
  POWER_ITEM_ID,
} from "./constants.js";

export function rateLabel(mode) {
  return {
    per_cycle: "Per Cycle",
    per_second: "Per Second",
    per_minute: "Per Minute",
  }[mode];
}

export function formatAmount(amount) {
  if (Math.abs(amount) < 0.00001) return "0";
  if (Number.isInteger(amount)) return String(amount);
  return Number(amount).toFixed(2).replace(/\.00$/, "").replace(/(\.\d*[1-9])0+$/, "$1");
}

export function titleCase(value) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase());
}

export function isPowerItem(itemId) {
  return itemId === POWER_ITEM_ID;
}

export function perMachineRate(targetItemId, baseRate, beltCapacity) {
  if (isPowerItem(targetItemId) || beltCapacity === null) {
    return baseRate;
  }
  return Math.min(baseRate, beltCapacity);
}

export function defaultBeltLabel(capacity) {
  if (capacity === null) {
    return "Unlimited";
  }
  const beltMk = BELT_CAPACITY_OPTIONS.indexOf(capacity) + 1;
  return `Mk ${beltMk} (${capacity}/min)`;
}

export function scaledAmount(amount, duration, rateMode) {
  if (rateMode === "per_cycle") return amount;
  if (rateMode === "per_second") return amount / duration;
  return (amount * 60) / duration;
}

export function amountSubtitle(verb, amount, duration, rateMode) {
  const scaled = formatAmount(scaledAmount(amount, duration, rateMode));
  const unit = { per_cycle: "per cycle", per_second: "/s", per_minute: "/min" }[rateMode];
  return `${verb} ${scaled} ${unit}`;
}

export function plannerEntryAmount(entry) {
  return formatAmount(entry.amount_per_minute);
}

export function clampPercentage(value) {
  return Math.max(0, Math.min(100, value));
}

export function clampZoom(zoom) {
  return Math.min(Math.max(zoom, MIN_ZOOM), MAX_ZOOM);
}
