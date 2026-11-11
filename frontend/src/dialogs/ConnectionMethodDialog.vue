<script>
import { useDashboard } from '../state/context'
export default { setup: useDashboard }
</script>

<template>
<div class="scrim" role="dialog" aria-modal="true" aria-labelledby="method-ask-title" v-dialog="() => { methodAsk=null }" @click.self="methodAsk=null">
      <div class="modal" style="padding:16px;width:min(560px,94vw)">
        <h3 id="method-ask-title" style="margin:0 0 6px">Kết nối {{methodAsk.provider.display_name}}</h3>
        <p class="sub" style="margin:0">Chọn cách thức kết nối tài khoản này. Bạn có thể bổ sung phương thức khác bất kỳ lúc nào.</p>
        <div class="method-grid" role="radiogroup" :aria-label="'How to connect '+methodAsk.provider.display_name">
          <label v-for="method in methodAsk.provider.authorization_methods" :key="method.name"
                 :class="['method-card',{on:methodAsk.selected===method.name,off:!method.configured}]">
            <input type="radio" name="authorization-method" :value="method.name" v-model="methodAsk.selected"
                   :disabled="!method.configured"/>
            <span class="method-copy">
              <span class="method-title">
                <b>{{method.display_name}}</b>
                <span v-if="isRecommendedMethod(methodAsk.provider,method)" class="chip ok">Khuyên dùng</span>
                <span v-if="method.in_review" class="chip warn">Đang duyệt</span>
                <span v-if="!method.configured" class="chip warn">Chưa cấu hình</span>
              </span>
              <span class="sub">{{method.description}}</span>
              <span v-if="method.consent_notice && methodAsk.selected===method.name" class="sub">{{method.consent_notice}}</span>
            </span>
          </label>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px">
          <button class="btn sm" @click="methodAsk=null">{{t('common.cancel') || 'Hủy'}}</button>
          <button class="btn sm primary" :disabled="connBusy || !selectedMethod(methodAsk) || !selectedMethod(methodAsk).configured"
                  @click="continueMethod()">Tiếp tục</button>
        </div>
      </div>
    </div>
</template>
