<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="share-dialog-title" aria-modal="true" v-dialog="() => { share.on=false }" @click.self="share.on=false">
      <div class="modal" style="width:min(560px,95vw)"><div class="hd"><b id="share-dialog-title">Chia sẻ “{{detail.name}}”</b><button class="btn sm ico" @click="share.on=false" aria-label="Đóng">✕</button></div>
        <div style="padding:16px 18px">
          <template v-if="share.sent">
            <p class="explain">✓ Đã gửi thư mời tới <b>{{share.sent.email}}</b> — nút trong email sẽ đăng nhập và chuyển họ thẳng tới trang này.</p>
            <p class="sub" style="margin:0 0 8px">Hoặc gửi trực tiếp liên kết này — liên kết đã điền sẵn email; khi đăng nhập, lời mời sẽ tự động được chấp nhận:</p>
            <pre class="code" style="white-space:pre-wrap;word-break:break-all">{{shareInviteUrl}}</pre>
            <div style="margin-top:12px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
              <button class="btn primary" @click="copyDetail(shareInviteUrl,'sharecopy')">⧉ {{detailCopied==='sharecopy'?'Đã chép!':'Sao chép liên kết mời'}}</button>
              <span class="sub" style="margin:0;font-size:12px">mã dự phòng: <span class="mono">{{share.sent.code}}</span> (<span class="mono">treg org join</span>)</span>
            </div>
          </template>
          <template v-else>
            <p class="explain">Đồng nghiệp đã có trong đội ngũ? Chỉ cần gửi liên kết trang (⧉ Sao chép liên kết). Biểu mẫu này dùng để mời thành viên <b>mới</b> vào đội ngũ.</p>
            <div v-if="share.member" class="tut-notice" style="margin:0 0 10px"><b>{{share.member.email}}</b> đã là thành viên — chỉ cần gửi đường dẫn trang mà không cần mời lại.</div>
            <div class="field" style="margin-bottom:10px"><input v-model="share.email" type="email" placeholder="dongnghiep@congty.com" @keyup.enter="sendShare"/></div>
            <div style="margin-bottom:10px">
              <label style="display:flex;gap:6px;align-items:center;font-size:12.5px">Vai trò
                <select v-model="share.role" style="background:var(--panel2);border:1px solid var(--line);color:var(--ink);border-radius:6px;padding:4px 8px;font-family:var(--mono)">
                  <option value="viewer">người xem (chỉ sử dụng, không sửa)</option><option value="member">thành viên</option><option v-if="isOwner" value="admin">quản trị viên</option>
                </select>
              </label>
            </div>
            <div style="margin-bottom:10px">
              <label style="display:flex;gap:8px;align-items:center;font-size:12.5px;cursor:pointer">
                <input type="checkbox" v-model="share.full"/> Chia sẻ toàn quyền truy cập
              </label>
            </div>
            <p class="sub" style="margin:0 0 12px;font-size:12px">Toàn quyền truy cập = họ có thể thấy và sử dụng mọi công cụ đội ngũ đã đăng ký. Bỏ chọn để giới hạn họ chỉ truy cập {{detail.kind==='skill'?'kỹ năng này':'công cụ này'}}.</p>
            <div v-if="share.err" class="banner" style="margin:0 0 10px">{{share.err}}</div>
            <button class="btn primary" @click="sendShare" :disabled="share.busy">{{share.busy ? 'Đang gửi…' : 'Gửi lời mời'}}</button>
          </template>
        </div></div>
    </div>
</template>
