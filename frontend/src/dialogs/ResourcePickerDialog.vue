<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="resource-picker-dialog-title" aria-modal="true" v-dialog="() => { resPick=null }" @click.self="resPick=null">
      <div class="modal" style="padding:16px">
        <h3 id="resource-picker-dialog-title" style="margin:0 0 10px">Chọn {{resPick.label}}</h3>
        <p class="sub" v-if="resPick.scoped" style="margin:0 0 10px">Kết nối này chỉ áp dụng cho {{resPick.label}} này.
          Để sử dụng {{resPick.label}} khác, hãy thêm một kết nối tài khoản khác.</p>
        <p class="sub" v-else style="margin:0 0 10px">{{resPick.label}} mặc định mà Agent của bạn sẽ sử dụng.</p>
        <div v-if="resPick.loading" class="ttable-wrap">
          <div style="padding:22px;text-align:center;color:var(--muted);font-family:var(--mono);font-size:12.5px">
            <span class="spin" aria-hidden="true"></span> Đang truy vấn nhà cung cấp danh sách {{resPick.plural}} khả dụng…
          </div>
        </div>
        <div v-else-if="resPick.err" class="banner" style="margin:0 0 10px">{{resPick.err}}</div>
        <p class="sub" v-else-if="!resPick.rows.length" style="margin:0 0 10px">Không tìm thấy {{resPick.plural}} nào — tài khoản này có thể chưa được phân quyền.</p>
        <div class="ttable-wrap" v-else><table class="ttable">
          <tr v-for="r in resPick.rows" :key="r.id">
            <td class="tn"><b>{{r.label||r.id}}</b><span class="sub" style="display:block;font-size:11px">{{r.id}}</span></td>
            <td class="tx"><button class="btn sm" :class="{primary:r.id===resPick.selected}" @click="chooseResource(r)">{{r.id===resPick.selected?'✓ Đang dùng':'Chọn mục này'}}</button></td>
          </tr>
        </table></div>
        <div style="margin-top:12px;text-align:right"><button class="btn sm" @click="resPick=null">{{t('common.close') || 'Đóng'}}</button></div>
      </div>
    </div>
</template>
