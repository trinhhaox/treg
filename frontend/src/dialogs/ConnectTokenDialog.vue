<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="connect-token-dialog-title" aria-modal="true" v-dialog="() => { tokenAsk=null }" @click.self="tokenAsk=null">
      <div class="modal" style="padding:16px">
        <h3 id="connect-token-dialog-title" style="margin:0 0 6px"><span class="plogo-tile"><img class="plogo" :src="'/logos/'+tokenAsk.provider.service+'.svg'" alt="" aria-hidden="true" @error="$event.target.style.visibility='hidden'"></span>{{tokenAsk.conn ? ('Thay thế khóa ' + tokenAsk.provider.display_name) : ('Kết nối ' + tokenAsk.provider.display_name)}}</h3>
        <p class="sub" style="margin:0 0 12px">Bạn tự cấp khóa {{(tokenAsk.provider.token_label||'API key')}} riêng của mình — Treg lưu trữ mã hóa an toàn phía máy chủ và tự động gắn vào mỗi lượt gọi của Agent.</p>
        <a v-if="tokenAsk.provider.setup_url" class="btn sm primary" :href="tokenAsk.provider.setup_url"
           target="_blank" rel="noopener">{{tokenAsk.provider.setup_action_label||'Tạo ứng dụng / Lấy khóa ↗'}}</a>
        <ol style="margin:12px 0 0;padding-left:20px;color:var(--muted);font-size:12.5px;line-height:1.7">
          <li v-for="(st,i) in (tokenAsk.provider.setup_steps||[])" :key="i">{{st}}</li>
        </ol>
        <div style="margin-top:12px">
          <label class="labelcls" style="display:block;font-size:11px;color:var(--muted);margin-bottom:4px">{{tokenAsk.provider.token_label||'Khóa API / Token'}}</label>
          <input class="bindinput" style="width:100%" type="password" autocomplete="off"
                 :placeholder="tokenAsk.provider.token_placeholder || 'Dán khóa bí mật vào đây...'" v-model="tokenAsk.token"
                 @keyup.enter="submitToken"/>
        </div>
        <p v-if="tokenAsk.provider.setup_note" class="sub" style="margin:10px 0 0;font-size:11.5px">{{tokenAsk.provider.setup_note}}</p>
        <p v-if="tokenAsk.provider.probe_cost_micro" class="mk-notice" style="margin:10px 0 0">
          Xác thực khóa này sẽ thực hiện 1 cuộc gọi thử nghiệm tính phí bởi nhà cung cấp với chi phí {{money(tokenAsk.provider.probe_cost_micro)}}.
          Treg sẽ không tái sử dụng cuộc gọi này cho kiểm tra định kỳ.
        </p>
        <div v-if="tokenAsk.err" class="banner" style="margin-top:10px">{{tokenAsk.err}}</div>
        <div style="margin-top:14px;text-align:right;display:flex;gap:8px;justify-content:flex-end">
          <button class="btn sm" @click="tokenAsk=null">{{t('common.cancel') || 'Hủy'}}</button>
          <button class="btn sm primary" :disabled="!tokenAsk.token.trim()||tokenAsk.busy" @click="submitToken">
            {{tokenAsk.busy ? 'Đang xác thực…' : 'Kết nối'}}</button>
        </div>
      </div>
    </div>
</template>
