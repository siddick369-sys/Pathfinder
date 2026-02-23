/**
 * Modération de contenu — PathFinder
 * Détecte les mots inappropriés dans les formulaires et affiche un modal d'avertissement.
 */
(function () {
    /* ───────────────── Liste de mots interdits (regex) ───────────────── */
    const FORBIDDEN_PATTERNS = [
        // Insultes françaises courantes
        'con(nard|nasse)?', 'put(e|ain)', 'merde(ux)?', 'encul[eéè]',
        'sal(e|aud|ope)', 'idiot(e)?', 'cr[eéè]tin(e)?', 'imbécile',
        'abruti(e)?', 'débile', 'nique', 'ntm', 'fdp', 'tg',
        'batard', 'bâtard', 'p[eé]d[eé]', 'ta\\s*gueule',
        'ferme\\s*(ta|la)\\s*gueule', 'va\\s*te\\s*faire',
        'fils\\s*de\\s*p', 'ordure', 'pourriture', 'd[eé]gage',
        'casse[- ]toi', 'bouffon(ne)?', 'tocard(e)?',
        // Langage haineux
        'raciste', 'nègre', 'négro', 'bougnoule', 'youpin',
        // Menaces
        'je\\s*vais\\s*te\\s*(tuer|frapper|buter|tabasser)',
        'tu\\s*vas\\s*(mourir|crever|payer)',
        // Spam & harcèlement
        'arnaque', 'escro(c|quer)', 'spam',
    ];

    const FORBIDDEN_REGEX = new RegExp(
        '\\b(' + FORBIDDEN_PATTERNS.join('|') + ')\\b',
        'gi'
    );

    /* ───────────────── Créer le modal d'avertissement ───────────────── */
    function createModal() {
        if (document.getElementById('moderation-modal')) return;

        const overlay = document.createElement('div');
        overlay.id = 'moderation-modal';
        overlay.innerHTML = `
      <div class="mod-overlay" style="
        position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;
        display:flex;align-items:center;justify-content:center;
        opacity:0;transition:opacity 0.3s;pointer-events:none;
      ">
        <div class="mod-dialog" style="
          background:var(--bg-card,#fff);border-radius:16px;padding:32px;
          max-width:450px;width:90%;text-align:center;
          box-shadow:0 20px 60px rgba(0,0,0,0.2);
          transform:scale(0.9);transition:transform 0.3s;
        ">
          <div style="font-size:3rem;margin-bottom:12px;">⚠️</div>
          <h3 style="font-size:1.2rem;margin-bottom:8px;color:var(--text,#1a1a2e);">
            Contenu inapproprié détecté
          </h3>
          <p style="color:var(--text-secondary,#6b7280);font-size:0.9rem;margin-bottom:8px;">
            Votre message contient des termes qui ne respectent pas nos
            <strong>règles de bonne conduite</strong>.
          </p>
          <div id="mod-detected-words" style="
            background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);
            border-radius:8px;padding:10px 16px;margin:12px 0;
            font-size:0.8rem;color:#dc2626;font-weight:500;
            max-height:80px;overflow-y:auto;
          "></div>
          <p style="color:var(--text-secondary,#6b7280);font-size:0.8rem;margin-bottom:20px;">
            Merci de reformuler votre message avec respect. 🙏<br>
            Les contenus offensants peuvent entraîner la <strong>suspension de votre compte</strong>.
          </p>
          <div style="display:flex;gap:12px;justify-content:center;">
            <button id="mod-edit-btn" class="btn btn-primary btn-sm" style="min-width:130px;">
              ✏️ Modifier
            </button>
            <button id="mod-send-btn" class="btn btn-outline btn-sm" style="min-width:130px;opacity:0.6;">
              Envoyer quand même
            </button>
          </div>
        </div>
      </div>
    `;
        document.body.appendChild(overlay);
    }

    /* ───────────────── Afficher / masquer le modal ───────────────── */
    function showModal(detectedWords, onEdit, onSendAnyway) {
        createModal();
        const overlay = document.querySelector('#moderation-modal .mod-overlay');
        const dialog = document.querySelector('#moderation-modal .mod-dialog');
        const wordsEl = document.getElementById('mod-detected-words');

        // Afficher les mots détectés (masqués partiellement)
        const masked = [...new Set(detectedWords)].map(w => {
            if (w.length <= 3) return w[0] + '*'.repeat(w.length - 1);
            return w[0] + '*'.repeat(w.length - 2) + w[w.length - 1];
        });
        wordsEl.textContent = 'Mots détectés : ' + masked.join(', ');

        // Animer l'ouverture
        requestAnimationFrame(() => {
            overlay.style.opacity = '1';
            overlay.style.pointerEvents = 'auto';
            dialog.style.transform = 'scale(1)';
        });

        // Bouton Modifier
        const editBtn = document.getElementById('mod-edit-btn');
        const sendBtn = document.getElementById('mod-send-btn');

        function close() {
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
            dialog.style.transform = 'scale(0.9)';
            editBtn.replaceWith(editBtn.cloneNode(true));
            sendBtn.replaceWith(sendBtn.cloneNode(true));
        }

        editBtn.addEventListener('click', () => { close(); if (onEdit) onEdit(); });
        sendBtn.addEventListener('click', () => { close(); if (onSendAnyway) onSendAnyway(); });
        overlay.addEventListener('click', (e) => { if (e.target === overlay) { close(); if (onEdit) onEdit(); } });
    }

    /* ───────────────── Vérifier le texte ───────────────── */
    function checkContent(text) {
        const matches = text.match(FORBIDDEN_REGEX);
        return matches ? matches : [];
    }

    /* ───────────────── Attacher aux formulaires ───────────────── */
    function attachToForm(formSelector, textSelector) {
        const form = document.querySelector(formSelector);
        if (!form) return;

        const textarea = form.querySelector(textSelector || 'textarea');
        if (!textarea) return;

        // Highlight en temps réel
        textarea.addEventListener('input', function () {
            const words = checkContent(this.value);
            if (words.length > 0) {
                this.style.borderColor = '#ef4444';
                this.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.1)';
            } else {
                this.style.borderColor = '';
                this.style.boxShadow = '';
            }
        });

        // Intercepter la soumission
        form.addEventListener('submit', function (e) {
            const words = checkContent(textarea.value);
            if (words.length > 0 && !form.dataset.forceSubmit) {
                e.preventDefault();
                showModal(
                    words,
                    () => { textarea.focus(); },            // Modifier
                    () => { form.dataset.forceSubmit = '1'; form.submit(); }  // Envoyer quand même
                );
            }
        });
    }

    /* ───────────────── Initialisation ───────────────── */
    document.addEventListener('DOMContentLoaded', function () {
        // Blog : formulaire de commentaire
        attachToForm('.comment-form', 'textarea[name="content"]');

        // Contact : formulaire de contact
        attachToForm('#contact-form', 'textarea');
    });

    // Exposer pour usage externe
    window.PathFinderModeration = { checkContent, showModal, attachToForm };
})();
