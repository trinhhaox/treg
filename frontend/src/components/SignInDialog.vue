<script>
import { useDashboard } from '../state/context'
import BrandMark from './BrandMark.vue'
export default {
  components: { BrandMark }, setup: useDashboard,
  data: () => ({
    ssoChoices: [],
    ssoBusy: false,
    ssoMode: false,
    pwdMode: true,
    isRegister: false,
    passwordInput: '',
    confirmPasswordInput: '',
  }),
  computed: {
    hasAltMethods() {
      return !!(this.meta?.email_otp || this.meta?.github || this.meta?.google || this.meta?.sso);
    },
  },
  methods: {
    setSsoMode(enabled) {
      this.ssoMode = enabled
      this.pwdMode = false
      this.ssoChoices = []
      this.loginErr = ''
      this.emailStage = false
    },
    setPwdMode(enabled) {
      this.pwdMode = enabled
      this.ssoMode = false
      this.ssoChoices = []
      this.loginErr = ''
      this.emailStage = false
      this.isRegister = false
    },
    async doPasswordAction() {
      const acc = (this.emailInput || '').trim()
      if (!acc) {
        this.loginErr = this.t('auth.account_required') || 'Vui lòng nhập email hoặc số điện thoại.'
        return
      }
      if (!this.passwordInput) {
        this.loginErr = 'Vui lòng nhập mật khẩu.'
        return
      }
      if (this.isRegister) {
        if (this.passwordInput.length < 6) {
          this.loginErr = this.t('password.min_len_error') || 'Mật khẩu phải có tối thiểu 6 ký tự.'
          return
        }
        if (this.passwordInput !== this.confirmPasswordInput) {
          this.loginErr = this.t('password.mismatch_error') || 'Mật khẩu xác nhận không khớp.'
          return
        }
        await this.passwordRegister(this.passwordInput, acc)
      } else {
        await this.passwordLogin(this.passwordInput, acc)
      }
    },
    async ssoLogin() {
      const email = this.emailInput.trim()
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { this.loginErr = 'Enter your work email.'; return }
      this.ssoBusy = true; this.loginErr = ''; this.ssoChoices = []
      try {
        const response = await fetch('/auth/sso/discover', {
          method: 'POST', headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ email }),
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.detail || 'Could not find company sign-in.')
        this.ssoChoices = result.teams || []
        if (this.ssoChoices.length === 1) this.ssoGo(this.ssoChoices[0].slug)
        else if (!this.ssoChoices.length) this.loginErr = 'This email has no company SSO connection. Use another sign-in method or ask your IT admin for your company link.'
      } catch (error) { this.loginErr = error.message || 'Could not find company sign-in.' }
      finally { this.ssoBusy = false }
    },
    ssoGo(slug) {
      this._stashNext()
      location.href = `/auth/sso/${encodeURIComponent(slug)}/start`
    },
  },
}
</script>

<template>
<div v-if="demo.signin" class="lc-scrim open" @click.self="demo.signin=false">
    <div class="lc-modal" role="dialog" aria-modal="true" aria-label="Sign in" v-dialog="() => { demo.signin=false }">
      <button class="cls" @click="demo.signin=false" aria-label="Close">✕</button>
      <div style="font-size:22px;line-height:1"><BrandMark/></div>
      <h2 style="margin:8px 0 2px;font-family:var(--mono)">{{oauthSignin?'Sign in to continue connecting Treg':(invitePrefill?'Accept your invite':(shareGate?'Sign in to view it':(publicCatalog?t('auth.signin_title'):t('auth.signin_title'))))}}</h2>
      <p v-if="oauthSignin" class="sub">After sign-in, review the requested access before you approve it.</p>
      <p v-else-if="invitePrefill" class="sub">Sign in with <b>{{invitePrefill}}</b> and you'll drop straight into the team.</p>
      <p v-else-if="shareGate" class="sub">You'll land on “{{shareGate.name}}” right after.</p>
      <p v-else class="sub">{{t('auth.dialog_sub_default')}}</p>
      <div v-if="pwdMode">
        <label for="sign-in-email-pwd" class="sub" style="display:block;text-align:left;margin:14px 0 4px">{{t('auth.account_label')}}</label>
        <div class="field"><input id="sign-in-email-pwd" v-model="emailInput" type="text" autocomplete="username" :placeholder="t('auth.account_placeholder')" @input="loginErr=''" @keyup.enter="doPasswordAction"/></div>
        
        <label for="sign-in-password" class="sub" style="display:block;text-align:left;margin:10px 0 4px">{{t('auth.password_label')}}</label>
        <div class="field"><input id="sign-in-password" v-model="passwordInput" type="password" autocomplete="current-password" :placeholder="t('auth.password_placeholder')" @keyup.enter="doPasswordAction"/></div>

        <div v-if="isRegister" style="margin-top:10px">
          <label for="sign-in-confirm-password" class="sub" style="display:block;text-align:left;margin:0 0 4px">{{t('password.confirm_label')}}</label>
          <div class="field"><input id="sign-in-confirm-password" v-model="confirmPasswordInput" type="password" autocomplete="new-password" :placeholder="t('password.confirm_placeholder')" @keyup.enter="doPasswordAction"/></div>
        </div>

        <button class="btn primary" style="width:100%;margin-top:12px;display:flex;align-items:center;justify-content:center;gap:9px" @click="doPasswordAction" :disabled="busy">
          {{busy ? (isRegister ? t('auth.registering') : t('auth.logging_in')) : (isRegister ? t('auth.register_btn') : t('auth.signin_btn'))}}
        </button>

        <div style="margin-top:10px;text-align:center">
          <a href="#" class="sub" style="font-size:12px;text-decoration:underline" @click.prevent="isRegister=!isRegister;loginErr=''">
            {{ isRegister ? t('auth.already_have_account') : t('auth.need_account') }}
          </a>
        </div>
      </div>
      <div v-else-if="!emailStage">
        <label for="sign-in-email" class="sub" style="display:block;text-align:left;margin:14px 0 4px">{{t('auth.email_label')}}</label>
        <div class="field"><input id="sign-in-email" v-model="emailInput" type="email" autocomplete="email" data-captcha="email_start" :placeholder="t('auth.email_placeholder')" @input="ssoChoices=[];loginErr=''" @keyup.enter="ssoMode?ssoLogin():emailStart()"/></div>
        <button v-if="ssoMode" class="btn primary" style="width:100%;display:flex;align-items:center;justify-content:center;gap:9px" :disabled="ssoBusy" @click="ssoLogin"><img src="/media/signin/shield.svg" alt="" aria-hidden="true" style="width:17px;height:17px;filter:invert(1)"/>{{ssoBusy?'Finding company…':'Continue with SSO'}}</button>
        <button v-else class="btn primary" style="width:100%;display:flex;align-items:center;justify-content:center;gap:9px" @click="emailStart" :disabled="busy"><img src="/media/signin/mail.svg" alt="" aria-hidden="true" style="width:17px;height:17px;filter:invert(1)"/>{{busy?t('auth.sending'):t('auth.send_code')}}</button>
        <div v-if="ssoChoices.length > 1" style="margin-top:10px">
          <p class="sub">Choose your company team:</p>
          <button v-for="team in ssoChoices" :key="team.slug" class="btn" style="width:100%;margin-top:6px;display:flex;align-items:center;justify-content:center;gap:9px" @click="ssoGo(team.slug)"><img src="/media/signin/shield.svg" alt="" aria-hidden="true" style="width:17px;height:17px"/>{{team.name}} · {{team.slug}}</button>
        </div>
      </div>
      <div v-else>
        <p class="sub" style="font-size:11px;margin:2px 0 8px">{{t('auth.code_sent_to')}} <b>{{emailInput}}</b><span v-if="devCode"> · {{t('auth.dev_code')}} <b class="mono">{{devCode}}</b></span> · <a href="#" @click.prevent="emailStage=false">{{t('auth.change_email')}}</a></p>
        <div class="field"><input v-model="codeInput" inputmode="numeric" :placeholder="t('auth.code_placeholder')" @keyup.enter="emailVerify"/></div>
        <button class="btn primary" style="width:100%;display:flex;align-items:center;justify-content:center;gap:9px" @click="emailVerify" :disabled="busy"><img src="/media/signin/mail.svg" alt="" aria-hidden="true" style="width:17px;height:17px;filter:invert(1)"/>{{busy?t('auth.verifying'):t('auth.signin_btn')}}</button>
      </div>
      <div v-if="hasAltMethods" class="sub" style="margin:14px 0 8px;text-align:center">{{t('auth.or_signin_with')}}</div>
      <button v-if="meta.email_otp" class="btn" style="width:100%;padding:11px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:9px" @click="setPwdMode(!pwdMode)">{{pwdMode ? ('✉ ' + t('auth.login_with_code')) : ('🔑 ' + t('auth.login_with_password'))}}</button>
      <button v-if="meta.sso" class="btn" style="width:100%;padding:11px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:9px" @click="setSsoMode(!ssoMode)"><img :src="ssoMode?'/media/signin/arrow-left.svg':'/media/signin/shield.svg'" alt="" aria-hidden="true" style="width:17px;height:17px"/>{{ssoMode?t('auth.send_code'):t('auth.company_sso')}}</button>
      <button v-if="meta.github" class="btn" style="width:100%;padding:11px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:9px" @click="githubLogin"><img src="/media/recruit/github.svg" alt="" aria-hidden="true" style="width:17px;height:17px"/>GitHub</button>
      <button v-if="meta.google" class="btn" style="width:100%;padding:11px;margin-bottom:8px;display:flex;align-items:center;justify-content:center;gap:9px" @click="googleLogin"><img src="/media/aeo/logos/google.svg" alt="" aria-hidden="true" style="width:17px;height:17px"/>Google</button>
      <details v-if="!oauthSignin" style="margin-top:12px;text-align:left">
        <summary class="sub" style="cursor:pointer;text-align:center">{{t('auth.token_summary')}}</summary>
        <div class="field" style="margin-top:8px"><input v-model="tokenInput" type="password" placeholder="X-Treg-Token" @keyup.enter="addToken(tokenInput)"/></div>
        <button class="btn" style="width:100%" @click="addToken(tokenInput)" :disabled="busy">{{busy?t('auth.token_checking'):t('auth.token_btn')}}</button>
      </details>
      <div v-if="loginErr" class="banner" style="margin-top:12px">{{loginErr}}</div>
    </div>
  </div>
</template>
