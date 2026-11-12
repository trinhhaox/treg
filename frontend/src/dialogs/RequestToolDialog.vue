<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="request-tool-dialog-title" aria-modal="true" v-dialog="() => { reqAsk=false;reqErr='' }" @click.self="reqAsk=false;reqErr=''">
      <div class="modal" style="width:min(520px,95vw)"><div class="hd"><b id="request-tool-dialog-title">Yêu cầu bổ sung công cụ</b><button class="btn sm ico" @click="reqAsk=false;reqErr=''" aria-label="Đóng">✕</button></div>
        <div style="padding:16px 18px">
          <template v-if="!reqDone">
            <p class="explain" style="margin-top:0">Thiếu nhà cung cấp hoặc chức năng bạn cần? Yêu cầu sẽ được chuyển thẳng tới đội ngũ quản trị danh mục — công cụ được yêu cầu nhiều nhất sẽ được tích hợp trước tiên.</p>
            <div class="lbl" style="margin-top:14px">Công cụ / Tính năng cần thêm</div>
            <div class="field" style="margin:0"><input v-model="reqForm.capability" maxlength="200" placeholder="ví dụ: Ahrefs backlinks, tra giá vé máy bay, bình luận HN" @keyup.enter="submitToolRequest"/></div>
            <div class="lbl" style="margin-top:14px">Chi tiết <span style="text-transform:none;letter-spacing:0;color:var(--muted2)">— không bắt buộc</span></div>
            <div class="field" style="margin:0"><textarea v-model="reqForm.note" maxlength="2000" rows="3" placeholder="Mục đích bạn muốn dùng, hoặc đường dẫn tới tài liệu API" style="resize:vertical;min-width:0"></textarea></div>
            <template v-if="!me">
              <div class="lbl" style="margin-top:14px">Liên hệ <span style="text-transform:none;letter-spacing:0;color:var(--muted2)">— tùy chọn, để nhận thông báo khi có tính năng</span></div>
              <div class="field" style="margin:0"><input v-model="reqForm.contact" maxlength="200" placeholder="you@example.com"/></div>
            </template>
            <div v-if="reqErr" class="banner" style="margin-top:12px">{{reqErr}}</div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:18px">
              <button class="btn primary" @click="submitToolRequest" :disabled="reqBusy">{{reqBusy ? 'Đang gửi…' : 'Gửi yêu cầu'}}</button>
              <span class="sub" style="font-size:11.5px;margin:0">Chỉ mất 10 giây — không bắt buộc đăng nhập.</span>
            </div>
          </template>
          <template v-else>
            <div style="text-align:center;padding:18px 6px 8px">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="var(--accent, currentColor)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
              <p style="margin:12px 0 4px;font-weight:600">Đã tiếp nhận yêu cầu — cảm ơn bạn!</p>
              <p class="sub" style="margin:0 0 16px">Yêu cầu sẽ được xem xét và ưu tiên tích hợp sớm nhất.</p>
              <button class="btn" @click="reqAsk=false">Đóng</button>
            </div>
          </template>
        </div></div>
    </div>
</template>
