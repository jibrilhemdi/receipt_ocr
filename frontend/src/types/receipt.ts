export interface LineItem {
  id: number;
  name: string;
  quantity: number;
  unit_price: number | null;
  line_total: number | null;
}

export interface Receipt {
  id: number;
  merchant: string | null;
  total: number | null;
  currency: string | null;
  purchase_date: string | null;
  raw_text: string;
  extra_data: Record<string, any> | null;
  created_at: string;
  items: LineItem[];
}