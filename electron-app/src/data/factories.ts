import { AccountingSettings, GeneralSettings } from '@/typing/types';
import { Defaults } from '@/data/defaults';
import { currencies } from '@/data/currencies';

export const defaultSettings = (): GeneralSettings => ({
  floatingPrecision: Defaults.FLOATING_PRECISION,
  anonymizedLogs: Defaults.ANONYMIZED_LOGS,
  ethRpcEndpoint: Defaults.RPC_ENDPOINT,
  balanceSaveFrequency: Defaults.BALANCE_SAVE_FREQUENCY,
  dateDisplayFormat: Defaults.DEFAULT_DISPLAY_FORMAT,
  historicDataStart: Defaults.HISTORICAL_DATA_START,
  anonymousUsageAnalytics: Defaults.ANONYMOUS_USAGE_ANALYTICS,
  selectedCurrency: currencies[0]
});

export const defaultAccountingSettings = (): AccountingSettings => ({
  lastBalanceSave: 0,
  includeCrypto2Crypto: true,
  includeGasCosts: true,
  taxFreeAfterPeriod: null
});
