# billing.md

The billing client retries every outbound call 4 times, fixed 3s apart,
including on 4xx, because the processor is eventually consistent.
