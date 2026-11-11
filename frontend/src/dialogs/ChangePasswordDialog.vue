<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'

export default {
  setup: useDashboard,
  data: () => ({
    hasPassword: false,
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
    busy: false,
    err: '',
    success: '',
  }),
  computed: {
    t() {
      return t
    },
  },
  async mounted() {
    try {
      const data = await this.api('/auth/password/status')
      if (data) {
        this.hasPassword = !!data.has_password
      }
    } catch (e) {
      // ignore
    }
  },
  methods: {
    async submitChange() {
      this.err = ''
      this.success = ''

      if (!this.newPassword || this.newPassword.length < 6) {
        this.err = t('password.min_len_error')
        return
      }
      if (this.newPassword !== this.confirmPassword) {
        this.err = t('password.mismatch_error')
        return
      }
      if (this.hasPassword && !this.oldPassword) {
        this.err = t('password.enter_old_error')
        return
      }

      this.busy = true
      try {
        await this.api('/auth/password/change', {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
          },
          body: JSON.stringify({
            old_password: this.oldPassword,
            new_password: this.newPassword,
          }),
        })
        this.success = t('password.update_success')
        this.hasPassword = true
        this.oldPassword = ''
        this.newPassword = ''
        this.confirmPassword = ''
        setTimeout(() => {
          if (this.success) {
            this.changePasswordDialog = false
          }
        }, 1800)
      } catch (e) {
        this.err = e.detail || e.message || t('password.update_failed')
      } finally {
        this.busy = false
      }
    },
  },
}
</script>

<template>
<div class="scrim" role="dialog" aria-labelledby="change-pwd-title" aria-modal="true" v-dialog="() => { changePasswordDialog=false }" @click.self="changePasswordDialog=false">
  <div class="modal" style="width:min(420px,92vw)">
    <div class="hd">
      <b id="change-pwd-title">{{ hasPassword ? t('password.change_title') : t('password.set_title') }}</b>
      <button class="btn sm ico" aria-label="Close" @click="changePasswordDialog=false">✕</button>
    </div>
    <div style="padding:20px 18px 18px">
      <p class="sub" style="margin:0 0 16px;font-size:13px">
        {{ hasPassword ? t('password.change_desc') : t('password.set_desc') }}
      </p>

      <div v-if="hasPassword" style="margin-bottom:12px">
        <label class="sub" style="display:block;margin-bottom:4px;font-size:12px">{{ t('password.old_label') }}</label>
        <div class="field">
          <input v-model="oldPassword" type="password" :placeholder="t('password.old_placeholder')" autocomplete="current-password" />
        </div>
      </div>

      <div style="margin-bottom:12px">
        <label class="sub" style="display:block;margin-bottom:4px;font-size:12px">{{ t('password.new_label') }}</label>
        <div class="field">
          <input v-model="newPassword" type="password" :placeholder="t('password.new_placeholder')" autocomplete="new-password" />
        </div>
      </div>

      <div style="margin-bottom:16px">
        <label class="sub" style="display:block;margin-bottom:4px;font-size:12px">{{ t('password.confirm_label') }}</label>
        <div class="field">
          <input v-model="confirmPassword" type="password" :placeholder="t('password.confirm_placeholder')" autocomplete="new-password" @keyup.enter="submitChange" />
        </div>
      </div>

      <button class="btn primary" style="width:100%" :disabled="busy" @click="submitChange">
        {{ busy ? t('password.saving') : (hasPassword ? t('password.btn_update') : t('password.btn_set')) }}
      </button>

      <p v-if="err" class="banner" role="alert" style="margin:12px 0 0">{{ err }}</p>
      <div v-if="success" class="banner" role="status" style="margin:12px 0 0;border-color:rgba(25,208,232,0.4);color:var(--accent,#19D0E8)">{{ success }}</div>
    </div>
  </div>
</div>
</template>

