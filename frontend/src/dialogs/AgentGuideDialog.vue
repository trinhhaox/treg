<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="agent-guide-dialog-title" aria-modal="true" v-dialog="() => { capAsk=null }" @click.self="capAsk=null">
      <div class="modal" style="padding:16px">
        <h3 id="agent-guide-dialog-title" style="margin:0 0 6px">Kết nối {{capAsk.provider.display_name}}</h3>
        <p class="sub" style="margin:0 0 14px">Bạn muốn cho phép Agent thực hiện những quyền hạn gì với tài khoản này?
          Mở rộng quyền hạn sau này sẽ yêu cầu bạn cấp phép lại qua màn hình của nhà cung cấp.</p>
        <p v-if="capAsk.provider.consent_notice" class="mk-notice" style="margin:0 0 14px">{{capAsk.provider.consent_notice}}</p>
        <p v-if="capAsk.provider.metered" class="mk-notice" style="margin:0 0 14px">Các lượt gọi trên kết nối này sẽ được
          tính phí từ số dư đội ngũ — {{capAsk.provider.display_name}} tính phí theo mức sử dụng thực tế
          (đọc ~${{capAsk.provider.billed_rates.read_per_result_usd}}/kết quả,
          đăng bài ${{capAsk.provider.billed_rates.write_per_call_usd}},
          ${{capAsk.provider.billed_rates.write_with_link_usd}} khi bài viết có liên kết ngoài).
          Nếu kết nối ứng dụng lập trình viên của riêng bạn, bạn sẽ không bị tính phí này.</p>
        <div class="ttable-wrap"><table class="ttable">
          <tr v-for="cap in capOptions(capAsk)" :key="cap">
            <td style="white-space:normal"><b>{{capLabel(cap,capAsk)}}</b>
              <span v-if="capInReview(cap,capAsk)" class="chip warn" style="margin-left:6px">Đang duyệt</span>
              <span class="sub" style="display:block;font-size:11px;margin-top:3px">{{capHelp(cap,capAsk)}}</span></td>
            <td class="tx"><button class="btn sm" :class="{primary:cap===capDefault(capAsk)}"
                                    @click="chooseCapability(cap)">Chọn</button></td>
          </tr>
        </table></div>
        <div style="margin-top:12px;text-align:right"><button class="btn sm" @click="capAsk=null">Hủy</button></div>
      </div>
    </div>
</template>
