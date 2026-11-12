<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="top-up-dialog-title" aria-modal="true" v-dialog="() => { topupOpen=false }" @click.self="topupOpen=false">
      <div class="modal" style="padding:18px 20px;width:min(620px,94vw)">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <h3 id="top-up-dialog-title" style="margin:0">Nạp tín dụng vào tài khoản</h3>
          <button class="btn sm" @click="topupOpen=false" aria-label="Đóng">✕</button>
        </div>
        <p class="sub" style="margin:6px 0 14px">Chọn gói nạp tiền. Các gói lớn hơn nhận thêm tín dụng thưởng; bạn luôn có thể nạp thêm bất kỳ lúc nào.</p>
        <div class="fundgrid fundgrid-5">
          <button v-for="p in billing.topup.presets" :key="p" class="fundcard" :class="{sel:topupPick===p}" :disabled="billingBusy" @click="topupPick=p">
            <b>${{p}}</b>
            <span v-if="tierBonus(p)" style="color:var(--green)">+{{money(tierBonus(p))}} thưởng</span>
            <span v-else-if="refPresetBonus(p)" style="color:var(--green)">+{{money(refPresetBonus(p))}} thưởng</span>
          </button>
          <button class="fundcard" :class="{sel:topupPick==='other'}" :disabled="billingBusy" @click="pickOther()">
            <b>Khác</b>
          </button>
        </div>
        <div v-if="topupPick==='other'" style="margin-top:12px">
          <div style="display:flex;align-items:center;border:1px solid var(--line);border-radius:var(--rb);background:var(--bg);padding:0 14px">
            <span style="font-family:var(--mono);font-size:22px;color:var(--muted)">$</span>
            <input type="number" :min="billing.topup.min_usd" :max="billing.topup.max_usd" step="1" v-model.number="topupOther" placeholder="0" autocomplete="off" data-lpignore="true"
                   style="flex:1;border:0;background:transparent;color:var(--ink);font-family:var(--mono);font-size:22px;font-weight:700;padding:12px 8px;outline:none;min-width:0"/>
          </div>
          <p class="sub" style="margin:6px 0 0">Số USD nguyên, từ ${{billing.topup.min_usd}} đến ${{billing.topup.max_usd.toLocaleString()}}.</p>
        </div>

        <!-- Auto top-up. -->
        <div style="margin-top:14px;border:1px solid var(--line);border-radius:var(--rb);padding:10px 12px;background:var(--panel2)">
          <template v-if="billing.autotopup.enabled||billing.autotopup.consented_at">
            <template v-if="billing.autotopup.disabled_reason==='authentication_required'">
              <b style="font-size:12.5px">Tự động nạp tiền đang tạm dừng.</b>
              <span class="sub" style="margin:0"> Khoản nạp thủ công này sẽ kích hoạt lại tính năng sau khi thanh toán thành công.</span>
            </template>
            <template v-else>
              <b style="font-size:12.5px">Tự động nạp tiền đang {{billing.autotopup.enabled?'bật':'được cấu hình'}}.</b>
              <span class="sub" style="margin:0"> Quản lý hoặc tắt trong trang Thanh toán.</span>
            </template>
          </template>
          <template v-else>
            <label style="display:flex;gap:10px;align-items:flex-start;cursor:pointer">
              <span class="tswitch" style="margin-top:2px"><input type="checkbox" v-model="topupAuto"/><span class="knob"></span></span>
              <span>
                <b style="font-size:12.5px">Tự động nạp tiền {{topupAuto?'bật':'tắt'}}</b>
                <span class="sub" style="display:block;margin:2px 0 0">
                  <template v-if="topupAuto">Tôi ủy quyền cho Treg tự động trừ thẻ đã lưu <b>${{autoAmount}}</b> mỗi khi số dư giảm xuống dưới <b>${{autoThreshold}}</b>, tối đa <b>{{autoPerHour}}</b> lần mỗi giờ. Có thể hủy bất kỳ lúc nào.</template>
                  <template v-else>Các lượt gọi công cụ sẽ tạm dừng khi hết số dư. Bật tùy chọn này để AI Agent chạy liên tục không bị gián đoạn.</template>
                </span>
                <span v-if="maxBonusPct" class="sub" style="display:block;margin:4px 0 0">Tự động nạp tiền cũng nhận cùng mức thưởng. Tăng hạn mức nạp tại trang thanh toán để nhận tới <span style="color:var(--green)">+{{maxBonusPct}}%</span> mỗi lần nạp.</span>
              </span>
            </label>
          </template>
        </div>

        <div style="margin-top:14px;border:1px solid var(--line);border-radius:var(--rb);padding:10px 12px;font-family:var(--mono);font-size:12.5px">
          <div style="display:flex;justify-content:space-between"><span>Tín dụng nhận được</span><span v-if="!topupUsd">—</span><span v-else><b>{{money(topupUsd*1e6+topupBonusMicro)}}</b><span v-if="topupBonusMicro" class="sub" style="margin:0"> ({{money(topupUsd*1e6)}} + <span style="color:var(--green)">{{money(topupBonusMicro)}} thưởng</span>)</span></span></div>
          <div style="display:flex;justify-content:space-between;border-top:1px solid var(--line);margin-top:8px;padding-top:8px;font-weight:700"><span>Tổng thanh toán</span><span>{{topupUsd?money(topupUsd*1e6):'—'}}</span></div>
        </div>
        <p v-if="topupErr" class="sub" style="color:var(--red);margin:10px 0 0">{{topupErr}}</p>
        <p class="sub" style="margin:10px 0 0">Thanh toán bảo mật qua cổng Stripe. Số dư được cộng ngay khi giao dịch hoàn tất.</p>
        <div style="margin-top:14px;display:flex;justify-content:flex-end;gap:8px">
          <button class="btn" @click="topupOpen=false" :disabled="billingBusy">Hủy</button>
          <button class="btn primary" :disabled="billingBusy||!topupValid" @click="payTopup()">{{billingBusy?'Đang kết nối Stripe…':(topupUsd?'Thanh toán $'+topupUsd:'Thanh toán ngay')}}</button>
        </div>
      </div>
    </div>
</template>
