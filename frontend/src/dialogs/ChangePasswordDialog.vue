<script>
import { useDashboard } from '../state/context'
import { t } from '../state/i18n'

export default {
  setup: useDashboard,
  data: () => ({
    hasPassword: false,
    phoneInput: '',
    phoneBusy: false,
    phoneErr: '',
    phoneSuccess: '',
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
        this.phoneInput = data.phone || ''
      }
    } catch (e) {
      // ignore
    }
  },
  methods: {
    async submitPhoneUpdate() {
      this.phoneErr = ''
      this.phoneSuccess = ''
      this.phoneBusy = true
      try {
        const res = await this.api('/auth/phone/update', {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
          },
          body: JSON.stringify({
            phone: this.phoneInput,
          }),
        })
        this.phoneSuccess = t('password.phone_success') || 'Cập nhật số điện thoại thành công!'
        if (res && res.phone !== undefined) {
          this.phoneInput = res.phone
        }
        setTimeout(() => {
          this.phoneSuccess = ''
        }, 2500)
      } catch (e) {
        this.phoneErr = e.detail || e.message || t('password.phone_invalid')
      } finally {
        this.phoneBusy = false
      }
    },
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
            phone: this.phoneInput,
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
  <div class="modal" style="width:min(440px,94vw)">
    <div class="hd">
      <b id="change-pwd-title">{{ hasPassword ? t('password.change_title') : t('password.set_title') }}</b>
      <button class="btn sm ico" aria-label="Close" @click="changePasswordDialog=false">✕</button>
    </div>
    <div style="padding:20px 18px 18px">
      <!-- Section: Phone Binding -->
      <div style="margin-bottom:18px">
        <label class="sub" style="display:block;margin-bottom:4px;font-size:12px;font-weight:600">{{ t('password.phone_label') }}</label>
        <p class="sub" style="margin:0 0 8px;font-size:12px">
          {{ t('password.phone_desc') }}
        </p>
        <div style="display:flex;gap:8px">
          <div class="field" style="flex:1">
            <input v-model="phoneInput" type="tel" :placeholder="t('password.phone_placeholder')" @input="phoneErr=''" @keyup.enter="submitPhoneUpdate" />
          </div>
          <button class="btn sm" :disabled="phoneBusy" @click="submitPhoneUpdate">
            {{ phoneBusy ? '...' : t('password.phone_btn') }}
          </button>
        </div>
        <p v-if="phoneErr" class="banner" role="alert" style="margin:8px 0 0">{{ phoneErr }}</p>
        <div v-if="phoneSuccess" class="banner" role="status" style="margin:8px 0 0;border-color:rgba(25,208,232,0.4);color:var(--accent,#19D0E8)">{{ phoneSuccess }}</div>
      </div>

      <hr style="border:none;border-top:1px solid var(--line);margin:16px 0 18px" />

      <!-- Section: Password Management -->
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
